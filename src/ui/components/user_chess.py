from nicegui import ui
from functools import partial


class Chess:
    def __init__(self):
        self.board_row = 8
        self.board_col = 8
        self.start_pos = None
        self.turn = 'white'
        self.grid = None
        self.board = [
            ['rooks-white', 'knights-white', 'bishops-white', 'queen-white', 'king-white', 'bishops-white',
             'knights-white', 'rooks-white'],
            ['pawns-white', 'pawns-white', 'pawns-white', 'pawns-white', 'pawns-white', 'pawns-white', 'pawns-white',
             'pawns-white'],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            ['pawns-black', 'pawns-black', 'pawns-black', 'pawns-black', 'pawns-black', 'pawns-black', 'pawns-black',
             'pawns-black'],
            ['rooks-black', 'knights-black', 'bishops-black', 'queen-black', 'king-black', 'bishops-black',
             'knights-black', 'rooks-black']
        ]
        self.squares = [[None for _ in range(self.board_col)] for _ in range(self.board_row)]
        self.create_chessboard()

    def create_chessboard(self):
        self.grid = ui.grid(columns=8).classes('w-auto m-auto gap-0')
        with self.grid:
            for i in range(self.board_row):
                for j in range(self.board_col):
                    color = '#769656' if (i + j) % 2 == 0 else '#EEEED2'
                    with ui.element('div').style(
                            f'background-color: {color}; width: 96px; height: 96px;').on(
                        'click', partial(self.handle_square_click, i, j)) as square:

                        self.squares[i][j] = square  # Zapisujemy referencję do pola

                        piece = self.board[i][j]
                        if piece:
                            with square:  # Umieszczamy obrazek w elemencie square
                                ui.image(f'./img/{"white-pieces" if "white" in piece else "black-pieces"}/{piece}.png')

    def handle_square_click(self, i, j):
        piece = self.board[i][j]
        if self.start_pos is None:
            if piece and self.turn in piece:
                self.start_pos = (i, j)
                ui.notify(f'Wybrano figurę na ({i}, {j})', color='blue')
            else:
                ui.notify('Nie możesz ruszyć tej figury!', color='red')
        else:
            self.move_piece(*self.start_pos, i, j)
            self.start_pos = None

    def move_piece(self, start_row, start_col, end_row, end_col):
        if not self._is_valid_position(start_row, start_col) or not self._is_valid_position(end_row, end_col):
            ui.notify('Nieprawidłowy ruch!', color='red')
            return

        piece = self.board[start_row][start_col]
        target_piece = self.board[end_row][end_col]

        if target_piece and self.turn in target_piece:
            ui.notify('Nie możesz zbić własnej figury!', color='red')
            return

        # Przenoszenie figury
        self.board[start_row][start_col] = None
        self.board[end_row][end_col] = piece

        # Aktualizujemy tylko te dwa pola
        self.update_square(start_row, start_col)
        self.update_square(end_row, end_col)

        ui.notify(f'Przeniesiono {piece} na ({end_row}, {end_col})', color='blue')
        self.turn = 'black' if self.turn == 'white' else 'white'

    def update_square(self, row, col):
        square = self.squares[row][col]
        square.clear()  # Usuwamy poprzednią zawartość pola

        piece = self.board[row][col]
        if piece:
            with square:
                ui.image(f'./img/{"white-pieces" if "white" in piece else "black-pieces"}/{piece}.png')

    def _is_valid_position(self, i, j):
        return 0 <= i < self.board_row and 0 <= j < self.board_col
