import tkinter as tk
from tkinter import messagebox, simpledialog

import chess
import chess.pgn

from src.chessmasters.chess.fen_loader import parse_fen_csv

UNICODE_PIECES = {
    chess.PAWN: ("♙", "♟"),
    chess.ROOK: ("♖", "♜"),
    chess.KNIGHT: ("♘", "♞"),
    chess.BISHOP: ("♗", "♝"),
    chess.QUEEN: ("♕", "♛"),
    chess.KING: ("♔", "♚"),
}


class ChessGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Python Chess")
        self.board = chess.Board()
        self.selected = None
        self.buttons = {}
        self.mode = tk.StringVar(value="Human vs Human")
        self.ai_level = tk.IntVar(value=1)
        self.move_list = tk.Listbox(self.root, width=30)
        self.training_data = None
        self.training_index = 0
        self.current_best_move = None
        self.setup_ui()
        self.update_board()

    def load_training_csv(self):
        data = parse_fen_csv()
        if not data:
            return
        self.training_data = data
        # Start from first position
        self.training_index = 0
        fen, best_move = self.training_data[self.training_index]
        self.board.set_fen(fen)
        self.current_best_move = best_move

        self.selected = None
        self.update_board()
        messagebox.showinfo("Training", f"Training mode started!\nBest move for this position is hidden.")

    def setup_ui(self):
        top = tk.Frame(self.root)
        top.pack(side=tk.TOP, fill=tk.X)
        tk.Button(top, text="Load Training CSV", command=self.load_training_csv).pack(side=tk.LEFT)

        board_frame = tk.Frame(self.root)
        board_frame.pack(side=tk.LEFT)

        # Add column letters
        for col, letter in enumerate("abcdefgh"):
            lbl = tk.Label(board_frame, text=letter.upper(), font=("Arial", 10, "bold"))
            lbl.grid(row=0, column=col + 1)

        # Add row numbers
        for row, number in enumerate(range(8, 0, -1)):
            lbl = tk.Label(board_frame, text=str(number), font=("Arial", 10, "bold"))
            lbl.grid(row=row + 1, column=0)

        for r in range(8):
            for c in range(8):
                btn = tk.Button(
                    board_frame,
                    font=("Arial", 32),
                    width=2,
                    height=1,
                    command=lambda rc=(r, c): self.on_click(rc),
                )
                btn.grid(row=r + 1, column=c + 1)
                self.buttons[(r, c)] = btn

        right = tk.Frame(self.root)
        right.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(right, text="Moves").pack()
        self.move_list.pack(fill=tk.Y, expand=True)

    def coord_to_square(self, coord):
        r, c = coord
        file = c
        rank = 7 - r
        return chess.square(file, rank)

    def square_to_coord(self, sq):
        file = chess.square_file(sq)
        rank = chess.square_rank(sq)
        r = 7 - rank
        c = file
        return (r, c)

    def on_click(self, coord):
        sq = self.coord_to_square(coord)
        piece = self.board.piece_at(sq)
        if self.selected is None:
            if piece and piece.color == self.board.turn:
                self.selected = sq
                self.highlight_moves(sq)
        else:
            if sq == self.selected:
                self.selected = None
                self.update_board()
                return
            move = chess.Move(self.selected, sq)
            if move in self.board.legal_moves:
                if self.is_promotion(move):
                    promo = self.ask_promotion()
                    if promo is None:
                        self.selected = None
                        self.update_board()
                        return
                    move.promotion = promo
                self.board.push(move)
                if self.training_data and self.current_best_move:
                    user_move = move.uci()
                    if user_move == self.current_best_move:
                        messagebox.showinfo("Result", "CORRECT move!")
                    else:
                        messagebox.showinfo("Result", f"INCORRECT (best was {self.current_best_move})")

                    # Advance to the next exercise
                    if self.training_data:
                        self.training_index += 1
                        if self.training_index < len(self.training_data):
                            fen, best_move = self.training_data[self.training_index]
                            self.board.set_fen(fen)
                            self.current_best_move = best_move
                            self.update_board()
                        else:
                            messagebox.showinfo("Training", "All positions completed!")
                            self.training_data = None

                self.selected = None
                self.record_move()
                self.update_board()
                self.after_move()
            else:
                if piece and piece.color == self.board.turn:
                    self.selected = sq
                    self.highlight_moves(sq)
                else:
                    self.selected = None
                    self.update_board()

    def is_promotion(self, move):
        if self.board.piece_type_at(move.from_square) == chess.PAWN:
            to_rank = chess.square_rank(move.to_square)
            if to_rank == 0 or to_rank == 7:
                return True
        return False

    def ask_promotion(self):
        choices = {
            "q": chess.QUEEN,
            "r": chess.ROOK,
            "b": chess.BISHOP,
            "n": chess.KNIGHT,
        }
        ans = simpledialog.askstring("Promotion", "Choose promotion piece: q(r, b, n)")
        if not ans:
            return None
        ans = ans.lower().strip()
        return choices.get(ans, chess.QUEEN)

    def highlight_moves(self, from_sq):
        self.update_board()
        for m in self.board.legal_moves:
            if m.from_square == from_sq:
                coord = self.square_to_coord(m.to_square)
                btn = self.buttons[coord]
                btn.config(bg="#aaffaa")
        coord = self.square_to_coord(from_sq)
        self.buttons[coord].config(bg="#aaaaff")

    def update_board(self):
        for r in range(8):
            for c in range(8):
                btn = self.buttons[(r, c)]
                sq = self.coord_to_square((r, c))
                piece = self.board.piece_at(sq)
                bg = "#eeeedd" if (r + c) % 2 == 0 else "#769656"
                btn.config(text="", bg=bg, fg="black")
                if piece:
                    sym = UNICODE_PIECES[piece.piece_type][0 if piece.color == chess.WHITE else 1]
                    btn.config(text=sym)
        if self.board.is_check():
            king_sq = self.board.king(self.board.turn)
            coord = self.square_to_coord(king_sq)
            self.buttons[coord].config(bg="#ff8888")
        self.update_move_list()

    def record_move(self):
        self.move_list.delete(0, tk.END)
        moves = list(self.board.move_stack)
        san = []
        b = chess.Board()
        for m in moves:
            san.append(b.san(m))
            b.push(m)
        for i in range(0, len(san), 2):
            num = i // 2 + 1
            white = san[i]
            black = san[i + 1] if i + 1 < len(san) else ""
            self.move_list.insert(tk.END, f"{num}. {white} {black}")

    def update_move_list(self):
        pass

    def after_move(self):
        if self.board.is_game_over():
            res = self.board.result()
            reason = ""
            if self.board.is_checkmate():
                reason = "Checkmate"
            elif self.board.is_stalemate():
                reason = "Stalemate"
            elif self.board.is_insufficient_material():
                reason = "Insufficient material"

            game = chess.pgn.Game()
            game.headers["Event"] = "Python Chess"
            game.headers["Result"] = res

            node = game
            temp_board = chess.Board()
            for move in self.board.move_stack:
                node = node.add_variation(move)
                temp_board.push(move)

            messagebox.showinfo("Game Over", f"Result: {res} ({reason})")
            return

    def evaluate(self):
        vals = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0,
        }
        s = 0
        for sq in chess.SQUARES:
            p = self.board.piece_at(sq)
            if p:
                v = vals[p.piece_type]
                s += v if p.color == chess.WHITE else -v
        return s

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ChessGUI()
    app.run()
