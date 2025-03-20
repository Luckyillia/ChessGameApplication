from nicegui import ui
from functools import partial
from collections import defaultdict
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
        self.white_captured = []
        self.black_captured = []
        self.last_move = None  # Dodaj śledzenie ostatniego ruchu
        self.create_chessboard()


    def initialize_board(self):
        return [
            [Rook('white', 0, 0), Knight('white', 0, 1), Bishop('white', 0, 2), Queen('white', 0, 3),
             King('white', 0, 4), Bishop('white', 0, 5), Knight('white', 0, 6), Rook('white', 0, 7)],
            [Pawn('white', 1, i, self) for i in range(8)],
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [Pawn('black', 6, i, self) for i in range(8)],
            [Rook('black', 7, 0), Knight('black', 7, 1), Bishop('black', 7, 2), Queen('black', 7, 3),
             King('black', 7, 4), Bishop('black', 7, 5), Knight('black', 7, 6), Rook('black', 7, 7)]
        ]

    def create_chessboard(self):
        self.grid = ui.grid(columns=8).classes('w-auto m-auto gap-0')
        with self.grid:
            for i in range(self.board_row):
                for j in range(self.board_col):
                    color = '#769656' if (i + j) % 2 == 0 else '#EEEED2'
                    
                    # Make the background div non-interactive
                    with ui.element('div').style(f'background-color: {color}; width: 100px; height: 100px;').on(
                            'click', partial(self.handle_square_click, i, j)) as square:
                        
                        self.squares[i][j] = square
                        piece = self.board[i][j]
                        if piece:
                            piece_type = piece.__class__.__name__.lower()
                            piece_color = piece.color
                            image_path = f'./src/img/{piece_color}-pieces/{piece_type}-{piece_color}.png'

                            # Make the chess pieces interactive
                            with square:
                                ui.image(image_path).style('pointer-events: all;')  # Allow clicks on the piece image
        self.update_captured_pieces()



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

            # 🔥 Poprawne wywołanie available_moves 🔥
            if (i, j) in piece.available_moves(self.board, self.last_move):
                self.move_piece(start_row, start_col, i, j)
            else:
                ui.notify('Nieprawidłowy ruch!', color='red')
            self.start_pos = None

    def move_piece(self, start_row, start_col, end_row, end_col):
        piece = self.board[start_row][start_col]
        target_piece = self.board[end_row][end_col]

        # Sprawdź, czy ruch jest dozwolony
        if (end_row, end_col) not in piece.available_moves(self.board, self.last_move):
            ui.notify('Nieprawidłowy ruch!', color='red')
            return

        # Jeśli ruch dotyczy króla, sprawdź, czy ruch jest bezpieczny
        if isinstance(piece, King):
            if not self.is_move_safe(start_row, start_col, end_row, end_col):
                ui.notify('Nie możesz wykonać tego ruchu, bo twój król będzie w szachu!', color='red')
                return

        # Symulacja ruchu, aby sprawdzić, czy król nie będzie w szachu
        original_piece = self.board[end_row][end_col]
        original_x, original_y = piece.x, piece.y  # 🔥 Zapisanie oryginalnych współrzędnych

        # Aktualizacja współrzędnych figury podczas symulacji
        piece.x, piece.y = end_row, end_col  # 🔥 Aktualizacja!
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None

        if self.isCheck(piece.color):
            # Cofnięcie symulacji
            self.board[start_row][start_col] = piece
            self.board[end_row][end_col] = original_piece
            piece.x, piece.y = original_x, original_y  # 🔥 Przywrócenie współrzędnych
            ui.notify('Nie możesz wykonać tego ruchu, bo twój król będzie w szachu!', color='red')
            return

        # Przywrócenie planszy i współrzędnych przed wykonaniem ruchu
        self.board[start_row][start_col] = piece
        self.board[end_row][end_col] = original_piece
        piece.x, piece.y = original_x, original_y  # 🔥 Przywrócenie współrzędnych

        # Sprawdzenie en passant
        if isinstance(piece, Pawn) and start_col != end_col and target_piece is None:
            captured_pawn = self.board[start_row][end_col]
            if isinstance(captured_pawn, Pawn) and captured_pawn.color != piece.color:
                self.board[start_row][end_col] = None  # Usunięcie zbitego pionka
                if captured_pawn.color == 'white':
                    self.white_captured.append(captured_pawn)
                else:
                    self.black_captured.append(captured_pawn)
                self.update_square(start_row, end_col)  # Aktualizacja planszy

        # Normalne bicie
        elif target_piece:
            if target_piece.color == 'white':
                self.white_captured.append(target_piece)
            else:
                self.black_captured.append(target_piece)

        # Wykonanie ruchu
        self.board[start_row][start_col] = None
        if isinstance(piece, Pawn):
            piece.move_piece(end_row, end_col, self.board)
        else:
            piece.move_piece(end_row, end_col)
        self.board[end_row][end_col] = piece

        # Aktualizacja planszy
        self.update_square(start_row, start_col)
        self.update_square(end_row, end_col)

        # Zmiana tury
        self.turn = 'black' if self.turn == 'white' else 'white'

        # Sprawdzenie szacha po ruchu
        if self.isCheck(self.turn):  # Sprawdzamy szach dla przeciwnika
            ui.notify(f'{self.turn.capitalize()} king is in check!', color='red')

        ui.notify(f'Przeniesiono {piece.__class__.__name__} na ({end_row}, {end_col})', color='blue')

        # Aktualizacja zbitych figur
        self.update_captured_pieces()

        # Zapamiętanie ostatniego ruchu
        self.last_move = (piece, (start_row, start_col), (end_row, end_col))


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

    def update_captured_pieces(self):
        # Sprawdzenie czy siatki już istnieją, jeśli nie, utworzenie nowych
        if not hasattr(self, 'captured_white_grid'):
            self.captured_white_grid = ui.grid(columns=4).classes('w-auto m-auto gap-0').style(
                'position: absolute; top: 50%; right: 0; transform: translateY(-50%); display: grid; grid-template-columns: repeat(4, 1fr); direction: rtl;'
            )
        if not hasattr(self, 'captured_black_grid'):
            self.captured_black_grid = ui.grid(columns=4).classes('w-auto m-auto gap-0').style(
                'position: absolute; top: 50%; left: 0; transform: translateY(-50%);'
            )

        # Czyszczenie poprzednich elementów
        self.captured_white_grid.clear()
        self.captured_black_grid.clear()

        # Aktualizacja białych zbitych figur (od prawej do lewej)
        with self.captured_white_grid:
            for piece in reversed(self.white_captured):
                with ui.element('div').style('width: 80px; height: 80px;').classes('m-auto'):
                    piece_type = piece.__class__.__name__.lower()
                    image_path = f'./src/img/white-pieces/{piece_type}-white.png'
                    ui.image(image_path)

        # Aktualizacja czarnych zbitych figur (od lewej do prawej)
        with self.captured_black_grid:
            for piece in self.black_captured:
                with ui.element('div').style('width: 80px; height: 80px;').classes('m-auto'):
                    piece_type = piece.__class__.__name__.lower()
                    image_path = f'./src/img/black-pieces/{piece_type}-black.png'
                    ui.image(image_path)

    def isCheck(self, color):
        """
        Sprawdza, czy król danego koloru jest w szachu.
        :param color: Kolor króla ('white' lub 'black')
        :return: True, jeśli król jest w szachu, False w przeciwnym razie
        """
        king_pos = None
        for row in self.board:
            for piece in row:
                if isinstance(piece, King) and piece.color == color:
                    king_pos = (piece.x, piece.y)
                    break
            if king_pos:
                break

        if not king_pos:
            return False

        # Sprawdzamy, czy jakakolwiek figura przeciwnika może zaatakować króla
        opponent_color = 'black' if color == 'white' else 'white'
        for row in self.board:
            for piece in row:
                if piece and piece.color == opponent_color:
                    if self.canSeeKing(king_pos, piece):
                        return True

        return False

    def canSeeKing(self, king_pos, piece):
        """
        Sprawdza, czy dana figura może zaatakować króla.
        :param king_pos: Pozycja króla (x, y)
        :param piece: Figura, która może atakować króla
        :return: True, jeśli figura może zaatakować króla, False w przeciwnym razie
        """
        if not piece:
            return False

        # Sprawdzamy, czy król znajduje się na liście dostępnych ruchów figury
        if king_pos in piece.available_moves(self.board, self.last_move):
            return True

        # Dodatkowe sprawdzenie dla pionków (specjalne zasady bicia)
        if isinstance(piece, Pawn):
            direction = 1 if piece.color == 'white' else -1
            x, y = piece.x, piece.y
            # Sprawdzamy, czy król znajduje się na polu bicia pionka
            if (king_pos == (x + direction, y - 1)) or (king_pos == (x + direction, y + 1)):
                return True

        return False

    def is_move_safe(self, start_row, start_col, end_row, end_col):
        piece = self.board[start_row][start_col]
        target_piece = self.board[end_row][end_col]

        # Zapisanie oryginalnych współrzędnych
        original_x, original_y = piece.x, piece.y

        # Symulacja ruchu (aktualizacja pozycji na planszy i współrzędnych figury)
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None
        piece.x, piece.y = end_row, end_col  # 🔥 Aktualizacja współrzędnych!

        # Sprawdzenie, czy król jest w szachu po ruchu
        is_safe = not self.isCheck(piece.color)

        # Cofnięcie symulacji (przywrócenie planszy i współrzędnych)
        self.board[start_row][start_col] = piece
        self.board[end_row][end_col] = target_piece
        piece.x, piece.y = original_x, original_y  # 🔥 Przywrócenie oryginalnych współrzędnych!

        return is_safe