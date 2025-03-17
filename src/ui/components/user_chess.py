# user_chess.py
from nicegui import ui
from functools import partial
from src.ui.components.chess_pieces import King, Queen, Rook, Knight, Bishop, Pawn


class Chess:
    def __init__(self):
        self.board_row = 8
        self.board_col = 8
        self.start_pos = None
        self.turn = 'white'
        self.grid = None
        self.board = self.initialize_board()
        self.squares = [[None for _ in range(self.board_col)] for _ in range(self.board_row)]
        self.create_chessboard()

    def initialize_board(self):
        return [
            [Rook('white', 0, 0), Knight('white', 0, 1), Bishop('white', 0, 2), Queen('white', 0, 3),
             King('white', 0, 4), Bishop('white', 0, 5), Knight('white', 0, 6), Rook('white', 0, 7)],
            [Pawn('white', 1, i) for i in range(8)],
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [Pawn('black', 6, i) for i in range(8)],
            [Rook('black', 7, 0), Knight('black', 7, 1), Bishop('black', 7, 2), Queen('black', 7, 3),
             King('black', 7, 4), Bishop('black', 7, 5), Knight('black', 7, 6), Rook('black', 7, 7)]
        ]

    def create_chessboard(self):
        self.grid = ui.grid(columns=8).classes('w-auto m-auto gap-0')
        with self.grid:
            for i in range(self.board_row):
                for j in range(self.board_col):
                    color = '#769656' if (i + j) % 2 == 0 else '#EEEED2'
                    with ui.element('div').style(f'background-color: {color}; width: 96px; height: 96px;').on(
                            'click', partial(self.handle_square_click, i, j)) as square:
                        self.squares[i][j] = square
                        piece = self.board[i][j]
                        if piece:
                            piece_type = piece.__class__.__name__.lower()
                            piece_color = piece.color
                            image_path = f'./src/img/{piece_color}-pieces/{piece_type}-{piece_color}.png'

                            with square:
                                ui.image(image_path)

    def handle_square_click(self, i, j):
        piece = self.board[i][j]
        if self.start_pos is None:
            if piece and self.turn == piece.color:
                self.start_pos = (i, j)
                ui.notify(f'Wybrano figurę na ({i}, {j})', color='blue')
            else:
                ui.notify('Nie możesz ruszyć tej figury!', color='red')
        else:
            start_row, start_col = self.start_pos
            piece = self.board[start_row][start_col]
            if (i, j) in piece.available_moves(self.board):
                self.move_piece(start_row, start_col, i, j)
            else:
                ui.notify('Nieprawidłowy ruch!', color='red')
            self.start_pos = None

    def move_piece(self, start_row, start_col, end_row, end_col):
        piece = self.board[start_row][start_col]
        target_piece = self.board[end_row][end_col]
        if target_piece and piece.color == target_piece.color:
            ui.notify('Nie możesz zbić własnej figury!', color='red')
            return
        self.board[start_row][start_col] = None
        piece.move_piece(end_row, end_col)
        self.board[end_row][end_col] = piece
        self.update_square(start_row, start_col)
        self.update_square(end_row, end_col)
        self.turn = 'black' if self.turn == 'white' else 'white'
        ui.notify(f'Przeniesiono {piece.__class__.__name__} na ({end_row}, {end_col})', color='blue')

    def update_square(self, row, col):
        square = self.squares[row][col]
        square.clear()

        piece = self.board[row][col]
        if piece:
            piece_type = piece.__class__.__name__.lower()
            piece_color = piece.color
            image_path = f'./src/img/{piece_color}-pieces/{piece_type}-{piece_color}.png'

            with square:
                ui.image(image_path)