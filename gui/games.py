"""Offline mini-games for the PY-OS Tkinter desktop."""
import random
import tkinter as tk
from tkinter import ttk, messagebox

BG, PANEL, TILE, FG, MUTED, ACCENT = "#101827", "#182538", "#263a55", "#edf4ff", "#9db0c9", "#64d6b0"

class Games:
    def __init__(self, desktop):
        self.os = desktop

    def win(self, key, title, size="560x480"):
        w = self.os.window("game-" + key, title, size)
        if getattr(w, "_game_built", False):
            return None
        w._game_built = True
        return w

    def hub(self):
        w = self.win("hub", "Games", "440x520")
        if not w: return
        self.os.heading(w, "PY-OS Games", "Choose a game. Scroll to see the whole collection.")
        outer = tk.Frame(w, bg=PANEL)
        outer.pack(fill="both", expand=True, padx=10, pady=8)
        canvas = tk.Canvas(outer, bg=PANEL, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        grid = tk.Frame(canvas, bg=PANEL)
        window_id = canvas.create_window((0, 0), window=grid, anchor="nw")
        grid.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window_id, width=e.width))
        def wheel(event):
            canvas.yview_scroll(int(-event.delta / 120), "units")
        canvas.bind_all("<MouseWheel>", wheel)
        w.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>") if e.widget is w else None)
        games = [
            ("♟", "Chess", "Two-player chess with legal moves", self.chess),
            ("🐍", "Snake", "Eat food and avoid your tail", self.snake),
            ("⭕", "Tic-Tac-Toe", "Play against a friend", self.tictactoe),
            ("🔢", "2048", "Join the tiles to reach 2048", self.game2048),
            ("💣", "Minesweeper", "Find every safe square", self.minesweeper),
            ("🏓", "Pong", "Play against the computer", self.pong),
        ]
        for i, (icon, name, desc, fn) in enumerate(games):
            card = tk.Frame(grid, bg=TILE, padx=10, pady=8)
            card.grid(row=i//2, column=i%2, sticky="nsew", padx=5, pady=5)
            tk.Label(card, text=icon, bg=TILE, fg=ACCENT, font=("Sans", 24)).pack()
            tk.Label(card, text=name, bg=TILE, fg=FG, font=("Sans", 12, "bold")).pack()
            tk.Label(card, text=desc, bg=TILE, fg=MUTED, wraplength=150).pack(pady=4)
            tk.Button(card, text="Play", command=fn, bg=ACCENT, fg="#08231c",
                      relief="flat", padx=18).pack(pady=4)
        for col in range(2): grid.columnconfigure(col, weight=1)

    def game_controls(self, w, restart):
        """Shared keyboard shortcuts and visible controls for every game."""
        footer = tk.Frame(w, bg=PANEL)
        footer.pack(side="bottom", fill="x", padx=10, pady=8)
        tk.Label(footer, text="R = Restart     Q = Quit", bg=PANEL, fg=MUTED).pack(side="left")
        ttk.Button(footer, text="Restart", command=restart).pack(side="right", padx=(5, 0))
        ttk.Button(footer, text="Quit", command=w.destroy).pack(side="right")
        def keypress(event):
            key = event.keysym.lower()
            if key == "q":
                w.destroy()
            elif key == "r":
                restart()
        w.bind("<KeyPress>", keypress, add="+")
        w.focus_set()

    def chess(self):
        try:
            import chess
        except ImportError:
            messagebox.showerror("Chess unavailable", "Install the chess rules package with:\npython -m pip install --user python-chess", parent=self.os)
            return
        w = self.win("chess", "Chess", "560x620")
        if not w: return
        self.game_controls(w, lambda: (w.destroy(), w.after(50, self.chess)))
        board = chess.Board()
        selected = [None]
        status = tk.Label(w, bg=PANEL, fg=FG, font=("Sans", 11, "bold"))
        status.pack(pady=8)
        board_frame = tk.Frame(w, bg=PANEL); board_frame.pack(padx=12, pady=6)
        squares = {}
        symbols = {"K":"♔","Q":"♕","R":"♖","B":"♗","N":"♘","P":"♙",
                   "k":"♚","q":"♛","r":"♜","b":"♝","n":"♞","p":"♟"}
        def refresh():
            status.config(text=("White" if board.turn else "Black") + " to move" +
                              (" · Check!" if board.is_check() else ""))
            for sq in chess.SQUARES:
                f, r = chess.square_file(sq), chess.square_rank(sq)
                piece = board.piece_at(sq)
                color = "#f0d9b5" if (f+r)%2==0 else "#b58863"
                if selected[0] == sq: color = "#d6b84c"
                elif selected[0] is not None and chess.Move(selected[0], sq) in board.legal_moves: color = "#86a96b"
                squares[sq].config(text=symbols[piece.symbol()] if piece else "", bg=color)
            if board.is_checkmate(): status.config(text=("White" if not board.turn else "Black")+" wins by checkmate!")
            elif board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition():
                status.config(text="Draw!")
        def click(sq):
            if board.is_game_over(): return
            if selected[0] is None:
                p = board.piece_at(sq)
                if p and p.color == board.turn: selected[0] = sq
            else:
                move = chess.Move(selected[0], sq)
                if board.piece_at(selected[0]).piece_type == chess.PAWN and chess.square_rank(sq) in (0,7):
                    move = chess.Move(selected[0], sq, promotion=chess.QUEEN)
                if move in board.legal_moves: board.push(move)
                elif board.piece_at(sq) and board.piece_at(sq).color == board.turn: selected[0] = sq
                else: selected[0] = None
            refresh()
        for rank in range(7,-1,-1):
            for file in range(8):
                sq = chess.square(file, rank)
                b = tk.Button(board_frame, text="", font=("DejaVu Sans", 27), width=2, height=1,
                              relief="flat", command=lambda s=sq: click(s))
                b.grid(row=7-rank, column=file, sticky="nsew")
                squares[sq] = b
        for c in range(8): board_frame.columnconfigure(c, weight=1)
        ttk.Button(w, text="New game", command=lambda: (board.reset(), selected.__setitem__(0,None), refresh())).pack(pady=8)
        tk.Label(w, text="Two players · Tap a piece, then its destination · Pawns promote to queens",
                 bg=PANEL, fg=MUTED, wraplength=500).pack(pady=4)
        refresh()

    def snake(self):
        w = self.win("snake", "Snake", "480x540")
        if not w: return
        self.game_controls(w, lambda: (w.destroy(), w.after(50, self.snake)))
        score = tk.Label(w, text="Score: 0", bg=PANEL, fg=FG, font=("Sans", 12, "bold")); score.pack(pady=5)
        c = tk.Canvas(w, width=400, height=400, bg="#0b1422", highlightthickness=0); c.pack(padx=10,pady=6)
        cell, cols, rows = 20, 20, 20
        snake = [(8,10),(7,10),(6,10)]; direction=[(1,0)]; food=[14,10]; state={"over":False,"score":0}
        def draw():
            c.delete("all")
            c.create_rectangle(food[0]*cell+3,food[1]*cell+3,(food[0]+1)*cell-3,(food[1]+1)*cell-3,fill="#ff687a",outline="")
            for i,(x,y) in enumerate(snake):
                c.create_rectangle(x*cell+1,y*cell+1,(x+1)*cell-1,(y+1)*cell-1,fill=ACCENT if i==0 else "#319b80",outline="")
        def turn(dx,dy):
            if (dx,dy)!=(-direction[0][0],-direction[0][1]): direction[0]=(dx,dy)
        for key,vec in (("<Up>",(0,-1)),("<Down>",(0,1)),("<Left>",(-1,0)),("<Right>",(1,0))):
            w.bind(key,lambda e,v=vec:turn(*v))
        def tick():
            if state["over"] or not w.winfo_exists(): return
            dx,dy=direction[0]; head=(snake[0][0]+dx,snake[0][1]+dy)
            if head[0]<0 or head[0]>=cols or head[1]<0 or head[1]>=rows or head in snake[:-1]:
                state["over"]=True; score.config(text="Game over · Score: "+str(state["score"])); return
            snake.insert(0,head)
            if list(head)==food:
                state["score"]+=1; score.config(text="Score: "+str(state["score"]))
                empty=[(x,y) for x in range(cols) for y in range(rows) if (x,y) not in snake]
                if empty: food[:]=random.choice(empty)
            else: snake.pop()
            draw(); w.after(115,tick)
        draw(); w.focus_set(); tick()

    def tictactoe(self):
        w = self.win("tictactoe", "Tic-Tac-Toe", "360x430")
        if not w: return
        self.game_controls(w, lambda: (w.destroy(), w.after(50, self.tictactoe)))
        board=[""]*9; turn=["X"]; buttons=[]
        status=tk.Label(w,text="X's turn",bg=PANEL,fg=FG,font=("Sans",14,"bold"));status.pack(pady=12)
        grid=tk.Frame(w,bg=PANEL);grid.pack(expand=True)
        wins=((0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6))
        def check():
            for line in wins:
                if board[line[0]] and board[line[0]]==board[line[1]]==board[line[2]]: return board[line[0]]
            return "Draw" if all(board) else None
        def play(i):
            if board[i] or check(): return
            board[i]=turn[0];buttons[i].config(text=turn[0],fg=ACCENT if turn[0]=="X" else "#ff9aaf")
            result=check()
            if result: status.config(text="It's a draw!" if result=="Draw" else result+" wins!")
            else: turn[0]="O" if turn[0]=="X" else "X";status.config(text=turn[0]+"'s turn")
        for i in range(9):
            b=tk.Button(grid,text="",font=("Sans",26,"bold"),width=4,height=2,bg=TILE,fg=FG,relief="flat",command=lambda n=i:play(n))
            b.grid(row=i//3,column=i%3,padx=3,pady=3);buttons.append(b)
        def reset():
            board[:]=[""]*9;turn[0]="X";status.config(text="X's turn")
            for b in buttons:b.config(text="")
        ttk.Button(w,text="New game",command=reset).pack(pady=12)

    def game2048(self):
        w=self.win("2048","2048","390x480")
        if not w:return
        self.game_controls(w, lambda: (w.destroy(), w.after(50, self.game2048)))
        board=[[0]*4 for _ in range(4)];score=[0]
        label=tk.Label(w,text="Score: 0",bg=PANEL,fg=FG,font=("Sans",14,"bold"));label.pack(pady=8)
        grid=tk.Frame(w,bg="#344761",padx=5,pady=5);grid.pack(padx=10,pady=8)
        cells=[]
        for r in range(4):
            row=[]
            for c in range(4):
                l=tk.Label(grid,text="",width=5,height=2,bg=TILE,fg=FG,font=("Sans",17,"bold"))
                l.grid(row=r,column=c,padx=3,pady=3);row.append(l)
            cells.append(row)
        def spawn():
            empty=[(r,c) for r in range(4) for c in range(4) if not board[r][c]]
            if empty:
                r,c=random.choice(empty);board[r][c]=4 if random.random()<.1 else 2
        def draw():
            for r in range(4):
                for c in range(4):
                    v=board[r][c];cells[r][c].config(text=str(v) if v else "",bg=("#263a55" if not v else "#"+{2:"eee4da",4:"ede0c8",8:"f2b179",16:"f59563",32:"f67c5f",64:"f65e3b",128:"edcf72",256:"edcc61",512:"edc850",1024:"edc53f",2048:"edc22e"}.get(v,"edc22e")),fg="#182538" if v<8 else "#ffffff")
            label.config(text="Score: "+str(score[0]))
        def move(direction):
            old=[r[:] for r in board]
            for i in range(4):
                vals=[board[i][j] for j in range(4)] if direction in ("Left","Right") else [board[j][i] for j in range(4)]
                if direction in ("Right","Down"): vals.reverse()
                vals=[v for v in vals if v]
                out=[];j=0
                while j<len(vals):
                    if j+1<len(vals) and vals[j]==vals[j+1]:
                        out.append(vals[j]*2);score[0]+=vals[j]*2;j+=2
                    else:out.append(vals[j]);j+=1
                out+= [0]*(4-len(out))
                if direction in ("Right","Down"):out.reverse()
                for k,v in enumerate(out):
                    if direction in ("Left","Right"):board[i][k]=v
                    else:board[k][i]=v
            if board!=old:spawn();draw()
        for key in ("<Left>","<Right>","<Up>","<Down>"):
            w.bind(key,lambda e,k=key[1:-1]:move(k))
        def reset():
            for r in range(4):
                for c in range(4):board[r][c]=0
            score[0]=0;spawn();spawn();draw()
        ttk.Button(w,text="New game",command=reset).pack(pady=8)
        w.focus_set();reset()

    def minesweeper(self):
        w=self.win("minesweeper","Minesweeper","430x500")
        if not w:return
        self.game_controls(w, lambda: (w.destroy(), w.after(50, self.minesweeper)))
        n=9;mines=set(random.sample(range(n*n),10));opened=set();flags=set();buttons=[]
        status=tk.Label(w,text="Find the 10 hidden mines",bg=PANEL,fg=FG);status.pack(pady=8)
        grid=tk.Frame(w,bg=PANEL);grid.pack(padx=8,pady=8)
        def count(i):return sum(j in mines for j in (i-n-1,i-n,i-n+1,i-1,i+1,i+n-1,i+n,i+n+1) if 0<=j<n*n and abs(j%n-i%n)<=1)
        def reveal(i):
            if i in opened or i in flags:return
            if i in mines:
                status.config(text="Boom! New game to try again.")
                for j,b in enumerate(buttons):
                    if j in mines:b.config(text="✹",bg="#9e344b")
                return
            opened.add(i);v=count(i);buttons[i].config(text=str(v) if v else "",bg="#31465f",state="disabled")
            if not v:
                for j in (i-n-1,i-n,i-n+1,i-1,i+1,i+n-1,i+n,i+n+1):
                    if 0<=j<n*n and abs(j%n-i%n)<=1:reveal(j)
            if len(opened)==n*n-len(mines):status.config(text="You cleared the minefield!")
        def flag(i):
            if i in opened:return
            if i in flags:flags.remove(i);buttons[i].config(text="")
            else:flags.add(i);buttons[i].config(text="⚑")
        for i in range(n*n):
            b=tk.Button(grid,text="",width=3,height=1,bg=TILE,fg=FG,relief="flat",command=lambda j=i:reveal(j))
            b.bind("<Button-3>",lambda e,j=i:flag(j));b.grid(row=i//n,column=i%n,padx=1,pady=1);buttons.append(b)
        tk.Label(w,text="Tap to reveal · Right-click to flag",bg=PANEL,fg=MUTED).pack(pady=5)
        ttk.Button(w,text="New game",command=lambda:(w.destroy(),self.minesweeper())).pack(pady=8)

    def pong(self):
        w=self.win("pong","Pong","560x430")
        if not w:return
        self.game_controls(w, lambda: (w.destroy(), w.after(50, self.pong)))
        c=tk.Canvas(w,width=520,height=320,bg="#081321",highlightthickness=0);c.pack(padx=10,pady=8)
        score=[0,0];paddle=[130];ball=[260,160,3,2];running=[True]
        label=tk.Label(w,text="You 0  —  0 CPU",bg=PANEL,fg=FG,font=("Sans",13,"bold"));label.pack()
        c.create_line(260,0,260,320,fill="#31465f",dash=(5,5))
        player=c.create_rectangle(15,130,25,190,fill=ACCENT,outline="")
        cpu=c.create_rectangle(495,130,505,190,fill="#ff9aaf",outline="")
        dot=c.create_oval(252,152,268,168,fill="#ffffff",outline="")
        def key(e):
            if e.keysym=="Up":paddle[0]=max(0,paddle[0]-22)
            elif e.keysym=="Down":paddle[0]=min(260,paddle[0]+22)
            c.coords(player,15,paddle[0],25,paddle[0]+60)
        w.bind("<Up>",key);w.bind("<Down>",key);w.focus_set()
        def tick():
            if not running[0] or not w.winfo_exists():return
            x,y,dx,dy=ball
            x+=dx;y+=dy
            if y<8 or y>312:dy=-dy
            cy=c.coords(cpu);mid=(cy[1]+cy[3])/2
            if mid<y-8: c.move(cpu,0,4)
            elif mid>y+8:c.move(cpu,0,-4)
            if x<35 and paddle[0]-8<y<paddle[0]+68:dx=abs(dx)+.2
            if x>485 and cy[1]-8<y<cy[3]+8:dx=-abs(dx)-.2
            if x<0:score[1]+=1;x,y,dx,dy=260,160,3,2
            if x>520:score[0]+=1;x,y,dx,dy=260,160,-3,2
            ball[:]=[x,y,dx,dy];c.coords(dot,x-8,y-8,x+8,y+8)
            label.config(text=f"You {score[0]}  —  {score[1]} CPU")
            w.after(16,tick)
        tick()
