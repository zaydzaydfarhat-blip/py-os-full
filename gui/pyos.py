#!/usr/bin/env python3
"""PY-OS native desktop app for Linux: Tkinter windows on X11/XWayland."""
import ast, json, operator, platform, shutil, subprocess, tkinter as tk, os, shlex, posixpath, re, pty, fcntl, termios, struct, select, errno
from datetime import datetime
import signal

# Ctrl+Z should not suspend the Tk desktop and leave its X11 session half-alive.
if hasattr(signal, "SIGTSTP"):
    signal.signal(signal.SIGTSTP, signal.SIG_IGN)
from pathlib import Path
from tkinter import ttk, messagebox

BG, PANEL, PANEL2, FG, MUTED, ACCENT = "#101827", "#182538", "#22334b", "#edf4ff", "#9db0c9", "#64d6b0"
DATA = Path.home() / ".local/share/py-os-gui/notes.json"
OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
       ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
       ast.UAdd: operator.pos, ast.USub: operator.neg}

def calc(expr):
    def ev(n):
        if isinstance(n, ast.Expression): return ev(n.body)
        if isinstance(n, ast.Constant) and type(n.value) in (int, float): return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in OPS: return OPS[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in OPS: return OPS[type(n.op)](ev(n.operand))
        raise ValueError("Use basic arithmetic only")
    result = ev(ast.parse(expr, mode="eval"))
    if abs(result) > 10**100: raise ValueError("Number too large")
    return result

class PyOS(tk.Tk):
    def __init__(self):
        # Ask Xcursor for KDE Breeze when it is installed; X11 falls back otherwise.
        os.environ.setdefault("XCURSOR_THEME","Breeze")
        os.environ.setdefault("XCURSOR_SIZE","24")
        super().__init__()
        self.configure(cursor="left_ptr")
        self.title("PY-OS")
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
        # PY-OS is a self-contained desktop shell; app windows use PY-OS controls.
        self.overrideredirect(True)
        self.minsize(320, 360)
        self.configure(bg=BG)
        self.windows, self.notes = {}, self.load_notes()
        self.style()
        self.desktop()
        self.after(500, self.clock)
        self.open_app("Welcome")

    def style(self):
        s=ttk.Style(self)
        try: s.theme_use("clam")
        except tk.TclError: pass
        s.configure("TFrame",background=PANEL); s.configure("TLabel",background=PANEL,foreground=FG,font=("Sans",11))
        s.configure("Muted.TLabel",background=PANEL,foreground=MUTED)
        s.configure("TButton",background=PANEL2,foreground=FG,padding=8)
        s.map("TButton",background=[("active","#344761")])
        s.configure("TEntry",fieldbackground="#0d1726",foreground=FG)
        s.configure("Treeview",background="#0d1726",foreground=FG,fieldbackground="#0d1726",rowheight=26)

    def desktop(self):
        top=tk.Frame(self,bg="#111b2b"); top.pack(fill="x")
        tk.Label(top,text="PY-OS",bg="#111b2b",fg=ACCENT,font=("Sans",14,"bold")).pack(side="left",padx=14,pady=9)
        self.time=tk.Label(top,bg="#111b2b",fg=MUTED); self.time.pack(side="right",padx=14)

        # Full-screen illustrated neon-night wallpaper, drawn at any window size.
        self.desktop_canvas=tk.Canvas(self,bg="#080f36",highlightthickness=0)
        self.desktop_canvas.pack(fill="both",expand=True)
        self.desktop_canvas.bind("<Configure>",self.draw_wallpaper)
        self.desktop_canvas.bind("<Configure>",lambda e:self.draw_wallpaper(e),add="+")
        self.desktop_canvas.after(100,self.draw_wallpaper)

        title=tk.Label(self.desktop_canvas,text="✦  PY-OS  ✦",bg="#101a50",fg="#d9c4ff",
                       font=("Sans",25,"bold"),padx=18,pady=8)
        tagline=tk.Label(self.desktop_canvas,text="A better OS. For everyone.",bg="#101a50",
                         fg="#d5e7ff",font=("Sans",11,"bold"),padx=12,pady=5)
        self.desktop_canvas.create_window(24,18,anchor="nw",window=title)
        self.desktop_canvas.create_window(31,75,anchor="nw",window=tagline)

        grid=tk.Frame(self.desktop_canvas,bg="#101a50")
        apps=[("🏠","Welcome"),("🧮","Calculator"),("📁","Notes"),("⚙","System info"),("🎮","Games")]
        for i,(ico,name) in enumerate(apps):
            tk.Button(grid,text=ico+"\n"+name,command=lambda n=name:self.open_app(n),bg="#17265c",fg=FG,
                activebackground="#344a91",activeforeground=FG,relief="flat",width=12,height=3,
                font=("Sans",10),cursor="hand2").grid(row=i//2,column=i%2,padx=5,pady=5,sticky="nsew")
        self.desktop_canvas.create_window(24,135,anchor="nw",window=grid)

        bar=tk.Frame(self,bg="#111b2b"); bar.pack(fill="x",side="bottom")
        tk.Button(bar,text="⊞ Start",command=self.launcher,bg=ACCENT,fg="#08231c",relief="flat",
                  font=("Sans",10,"bold"),padx=16).pack(side="left",padx=10,pady=7)
        self.task_buttons=tk.Frame(bar,bg="#111b2b")
        self.task_buttons.pack(side="left",fill="x",expand=True,padx=6)
        tk.Label(bar,text="Native Linux desktop",bg="#111b2b",fg=MUTED).pack(side="right",padx=12)
        tk.Button(bar,text="↩ Leave",command=self.leave_desktop,bg="#a8324a",fg="#ffffff",
                  activebackground="#d0445d",activeforeground="#ffffff",relief="flat",
                  font=("Sans",10,"bold"),padx=12).pack(side="right",padx=8,pady=6)

    def leave_desktop(self):
        """Close the desktop; gui/start.sh cleans up the X11 server it started."""
        try:
            self.destroy()
        except tk.TclError:
            pass

    def draw_wallpaper(self,event=None):
        canvas=getattr(self,"desktop_canvas",None)
        if not canvas or not canvas.winfo_exists(): return
        w=max(320,canvas.winfo_width()); h=max(240,canvas.winfo_height())
        if getattr(self,"_wallpaper_size",None)==(w,h): return
        self._wallpaper_size=(w,h)
        canvas.delete("wallpaper")
        def hexmix(a,b,t):
            aa=[int(a[i:i+2],16) for i in (1,3,5)]
            bb=[int(b[i:i+2],16) for i in (1,3,5)]
            return "#"+"".join(f"{round(x+(y-x)*t):02x}" for x,y in zip(aa,bb))
        # Deep blue-to-purple sky.
        for y in range(0,h,5):
            canvas.create_rectangle(0,y,w,y+6,fill=hexmix("#050d2c","#30216f",y/h),outline="",tags="wallpaper")
        import random
        rng=random.Random(23)
        for _ in range(max(70,w*h//9000)):
            x=rng.randrange(w); y=rng.randrange(max(1,int(h*.62)))
            r=rng.choice((1,1,2,2,3))
            canvas.create_oval(x-r,y-r,x+r,y+r,fill=rng.choice(("#d8e8ff","#8dbbff","#c49aff")),outline="",tags="wallpaper")
        # Moon and soft halo.
        mx,my=w*.70,h*.20; mr=min(w,h)*.075
        canvas.create_oval(mx-mr*1.5,my-mr*1.5,mx+mr*1.5,my+mr*1.5,fill="#263e9a",outline="",tags="wallpaper")
        canvas.create_oval(mx-mr,my-mr,mx+mr,my+mr,fill="#e4e9ff",outline="#b8caff",width=2,tags="wallpaper")
        for i in range(9):
            rr=mr*(.12+i*.075)
            canvas.create_oval(mx-rr,my-rr,mx+rr,my+rr,fill=("#d2dcff" if i%2 else "#b8c8f0"),outline="",tags="wallpaper")
        # Layered mountains.
        canvas.create_polygon(0,h*.66,w*.18,h*.48,w*.34,h*.67,w*.53,h*.50,w*.72,h*.68,w*.88,h*.52,w,h*.66,w,h,0,h,
                              fill="#111b58",outline="",tags="wallpaper")
        canvas.create_polygon(0,h*.73,w*.23,h*.58,w*.42,h*.75,w*.62,h*.59,w*.82,h*.76,w,h*.62,w,h,0,h,
                              fill="#17256c",outline="",tags="wallpaper")
        # City skyline and glowing windows.
        base=h*.73
        for i in range(24):
            x=i*w/24; bw=w/24+2; bh=rng.uniform(h*.07,h*.22)
            canvas.create_rectangle(x,base-bh,x+bw,base,fill=rng.choice(("#101b55","#17266d","#20256d")),outline="",tags="wallpaper")
            for wy in range(int(base-bh+8),int(base-7),14):
                for wx in range(int(x+5),int(x+bw-3),10):
                    if rng.random()>.28:
                        canvas.create_rectangle(wx,wy,wx+3,wy+5,fill=rng.choice(("#54c9ff","#a17cff","#e28bff")),outline="",tags="wallpaper")
        # Reflective lake.
        canvas.create_rectangle(0,base,w,h,fill="#101c63",outline="",tags="wallpaper")
        for i in range(90):
            y=base+(h-base)*i/90
            x=rng.randrange(w); length=rng.randrange(max(4,int(w*.008)),max(8,int(w*.10)))
            canvas.create_line(x,y,min(w,x+length),y,fill=rng.choice(("#3042a5","#6250d1","#328ed1","#9b64e8")),width=rng.choice((1,2,3)),tags="wallpaper")
        # Little silhouetted cat watching the moonlit city.
        cx,cy=w*.69,h*.84; unit=min(w,h)*.045
        canvas.create_oval(cx-unit*1.2,cy-unit*.2,cx+unit*1.2,cy+unit*1.9,fill="#080d25",outline="#7762d6",width=2,tags="wallpaper")
        canvas.create_polygon(cx-unit,cy,cx-unit*.95,cy-unit*1.5,cx-unit*.15,cy-unit*.8,
                              cx+unit*.15,cy-unit*.8,cx+unit*.95,cy-unit*1.5,cx+unit,cy,
                              fill="#080d25",outline="#7762d6",width=2,tags="wallpaper")
        canvas.create_arc(cx+unit*.5,cy+unit,cx+unit*2.2,cy+unit*2.7,start=190,extent=250,
                          style="arc",outline="#080d25",width=max(4,int(unit*.5)),tags="wallpaper")
        canvas.create_line(cx-unit*.9,cy+unit*.1,cx+unit*.9,cy+unit*.1,fill="#a76aff",width=3,tags="wallpaper")
        canvas.create_text(w-18,h-14,anchor="se",text="Made by ChatGPT  •  Idea by Zayd",
                           fill="#d9c8ff",font=("Sans",9,"bold"),tags="wallpaper")

    def clock(self):
        self.time.config(text=datetime.now().strftime("%a %d %b  %H:%M:%S"))
        self.after(1000,self.clock)

    def window(self,key,title,size="600x420"):
        w=self.windows.get(key)
        if w and w.winfo_exists(): w.deiconify(); w.lift(); w.focus_force(); return w
        w=tk.Toplevel(self); w.title(title+" — PY-OS"); w.geometry(size); w.minsize(280,200); w.configure(bg=PANEL)
        # Center each new app window on the available screen.
        w.update_idletasks()
        sw, sh = w.winfo_screenwidth(), w.winfo_screenheight()
        ww, wh = w.winfo_width(), w.winfo_height()
        x, y = max(0, (sw - ww) // 2), max(0, (sh - wh) // 2)
        w.geometry(f"+{x}+{y}")
        self.windows[key]=w
        task_btn=tk.Button(self.task_buttons,text=title,command=lambda win=w:self.toggle_window(win),
            bg=PANEL2,fg=FG,activebackground="#344761",activeforeground=FG,
            relief="flat",bd=0,padx=10,pady=5,font=("Sans",9),cursor="hand2")
        task_btn.pack(side="left",padx=2,pady=4)
        w._pyos_task_button=task_btn
        w.protocol("WM_DELETE_WINDOW",w.destroy)
        w.bind("<Destroy>",lambda e,k=key,obj=w:self.remove_window(e,k,obj))

        # PY-OS window controls: minimize, maximize/restore, and close.
        w._pyos_maximized = False
        w._pyos_saved_geometry = None
        titlebar = tk.Frame(w, bg="#111b2b", height=38)
        titlebar.pack(fill="x", side="top")
        titlebar.pack_propagate(False)
        tk.Label(titlebar, text=title, bg="#111b2b", fg=FG,
                 font=("Sans", 10, "bold")).pack(side="left", padx=12)
        controls = tk.Frame(titlebar, bg="#111b2b")
        controls.pack(side="right", padx=5, pady=4)

        def minimize():
            # withdraw() works even when the X11 window manager does not
            # implement iconify/minimize hints (common in lightweight X11 setups).
            w.withdraw()

        def maximize():
            if not w._pyos_maximized:
                w._pyos_saved_geometry = w.geometry()
                sw, sh = w.winfo_screenwidth(), w.winfo_screenheight()
                w.geometry(f"{sw}x{sh}+0+0")
                w._pyos_maximized = True
                max_button.configure(text="❐")
            else:
                if w._pyos_saved_geometry:
                    w.geometry(w._pyos_saved_geometry)
                w._pyos_maximized = False
                max_button.configure(text="□")

        def control(label, command, hover):
            return tk.Button(controls, text=label, command=command, bg="#22334b",
                fg=FG, activebackground=hover, activeforeground=FG,
                relief="flat", bd=0, width=3, font=("Sans", 10, "bold"),
                cursor="hand2")

        control("—", minimize, "#344761").pack(side="left", padx=2)
        max_button = control("□", maximize, "#344761")
        max_button.pack(side="left", padx=2)
        control("×", w.destroy, "#b83b50").pack(side="left", padx=2)

        # Drag windows by grabbing anywhere on the custom title bar.
        def drag_start(event):
            w._pyos_drag_x=event.x_root-w.winfo_x()
            w._pyos_drag_y=event.y_root-w.winfo_y()
        def drag_move(event):
            if not w._pyos_maximized:
                w.geometry(f"+{event.x_root-w._pyos_drag_x}+{event.y_root-w._pyos_drag_y}")
        for part in (titlebar, *titlebar.winfo_children()):
            part.bind("<Button-1>",drag_start)
            part.bind("<B1-Motion>",drag_move)

        # Visible bottom-right resize handle works independently of the WM.
        grip=tk.Label(w,text="◢",bg=PANEL,fg=MUTED)
        grip.place(relx=1.0,rely=1.0,anchor="se",x=-3,y=-2)
        def resize_start(event):
            w._pyos_resize=(event.x_root,event.y_root,w.winfo_width(),w.winfo_height())
        def resize_move(event):
            if not w._pyos_maximized and hasattr(w,"_pyos_resize"):
                sx,sy,sw,sh=w._pyos_resize
                nw=max(280,sw+event.x_root-sx); nh=max(200,sh+event.y_root-sy)
                w.geometry(f"{nw}x{nh}")
        grip.bind("<Button-1>",resize_start)
        grip.bind("<B1-Motion>",resize_move)
        return w

    def toggle_window(self,w):
        if not w or not w.winfo_exists(): return
        # A taskbar click hides a visible window, or restores a hidden one.
        if w.state() in ("withdrawn","iconic"):
            w.deiconify(); w.lift(); w.focus_force()
        else:
            w.withdraw()

    def focus_window(self,w):
        if w and w.winfo_exists():
            w.deiconify(); w.lift(); w.focus_force()

    def remove_window(self,event,key,w):
        if event.widget is not w: return
        if self.windows.get(key) is w: self.windows.pop(key,None)
        button=getattr(w,"_pyos_task_button",None)
        if button:
            try: button.destroy()
            except tk.TclError: pass

    def heading(self,w,title,sub):
        tk.Label(w,text=title,bg=PANEL,fg=FG,font=("Sans",17,"bold")).pack(anchor="w",padx=15,pady=(14,4))
        tk.Label(w,text=sub,bg=PANEL,fg=MUTED,wraplength=650,justify="left").pack(anchor="w",padx=15,pady=(0,10))

    def open_app(self,name):
        key=name.lower().replace(" ","-")
        sizes={"Welcome":"600x390","Calculator":"340x450","Notes":"600x440","System info":"540x380","Games":"460x540"}
        w=self.window(key,name,sizes.get(name,"580x400"))
        if getattr(w,"built",False): return
        w.built=True
        if name=="Welcome":
            self.heading(w,"Welcome to PY-OS","A native Linux desktop. Your apps open in normal, movable and resizable windows.")
            for line in ("✓ Calculator with basic arithmetic","✓ Local notes saved on this device","✓ System information","✓ Movable and resizable app windows"):
                ttk.Label(w,text=line).pack(anchor="w",padx=20,pady=7)
        elif name=="Calculator": self.calculator(w)
        elif name=="Notes": self.notes_app(w)
        elif name=="System info": self.system(w)
        elif name=="Games":
            from games import Games
            Games(self).hub()
        w.lift()

    def launcher(self):
        w=self.window("launcher","PY-OS Start","300x350")
        if getattr(w,"built",False): return
        w.built=True
        for n in ("Welcome","Calculator","Notes","System info","Games"):
            ttk.Button(w,text=n,command=lambda x=n:self.open_app(x)).pack(fill="x",padx=12,pady=5)

    def calculator(self,w):
        display=tk.Entry(w,justify="right",font=("Sans",22),bg="#0d1726",fg=FG,insertbackground=FG,relief="flat")
        display.pack(fill="x",padx=12,pady=12,ipady=10); display.insert(0,"0")
        keys=["7","8","9","/","4","5","6","*","1","2","3","-","0",".","⌫","+","C","(",")","="]
        grid=tk.Frame(w,bg=PANEL); grid.pack(fill="both",expand=True,padx=10,pady=5)
        def press(k):
            cur=display.get()
            if k=="C": display.delete(0,"end")
            elif k=="⌫": display.delete(max(0,len(cur)-1),"end")
            elif k=="=":
                try: value=str(calc(cur)); display.delete(0,"end"); display.insert(0,value)
                except Exception: display.delete(0,"end"); display.insert(0,"Error")
            else:
                if cur=="0": display.delete(0,"end")
                display.insert("end",k)
        for i,k in enumerate(keys):
            tk.Button(grid,text=k,command=lambda x=k:press(x),bg=PANEL2,fg=FG,activebackground=ACCENT,
                      relief="flat",font=("Sans",15)).grid(row=i//4,column=i%4,sticky="nsew",padx=3,pady=3)
        for c in range(4): grid.columnconfigure(c,weight=1)
        for r in range(5): grid.rowconfigure(r,weight=1)

    def load_notes(self):
        try: return json.loads(DATA.read_text(encoding="utf-8"))
        except (OSError,ValueError): return {}

    def notes_app(self,w):
        self.heading(w,"Notes","Saved in ~/.local/share/py-os-gui/notes.json")
        row=tk.Frame(w,bg=PANEL); row.pack(fill="x",padx=12,pady=5)
        name=ttk.Entry(row); name.insert(0,"my-note"); name.pack(side="left",fill="x",expand=True,padx=(0,6))
        text=tk.Text(w,bg="#0d1726",fg=FG,insertbackground=FG,wrap="word",relief="flat")
        text.pack(fill="both",expand=True,padx=12,pady=7)
        choice=ttk.Combobox(w,values=sorted(self.notes),state="readonly"); choice.pack(fill="x",padx=12,pady=4)
        def load():
            key=choice.get()
            if key in self.notes:
                name.delete(0,"end"); name.insert(0,key); text.delete("1.0","end"); text.insert("1.0",self.notes[key])
        def save():
            key=name.get().strip()
            if not key: return
            self.notes[key]=text.get("1.0","end-1c")
            try:
                DATA.parent.mkdir(parents=True,exist_ok=True); DATA.write_text(json.dumps(self.notes,indent=2),encoding="utf-8")
                choice.configure(values=sorted(self.notes)); choice.set(key)
            except OSError as e: messagebox.showerror("Save failed",str(e),parent=w)
        ttk.Button(row,text="Save note",command=save).pack(side="right")
        ttk.Button(w,text="Load selected note",command=load).pack(anchor="e",padx=12,pady=4)

    def system(self,w):
        self.heading(w,"System information","Current Linux environment")
        vals=[("OS",platform.platform()),("Architecture",platform.machine()),("Python",platform.python_version()),
              ("Hostname",platform.node())]
        for k,v in vals:
            row=tk.Frame(w,bg=PANEL); row.pack(fill="x",padx=15,pady=7)
            tk.Label(row,text=k,width=13,anchor="w",bg=PANEL,fg=MUTED).pack(side="left")
            tk.Label(row,text=v,anchor="w",bg=PANEL,fg=FG,wraplength=380,justify="left").pack(side="left",fill="x",expand=True)

if __name__=="__main__":
    try: PyOS().mainloop()
    except tk.TclError as e:
        print("PY-OS could not open a graphical display:",e)
        print("Start your X11/XWayland desktop first.")
