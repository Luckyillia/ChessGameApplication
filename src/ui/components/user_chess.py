from nicegui import ui
from functools import partial
from src.ui.components.chess_pieces import King, Queen, Rook, Knight, Bishop, Pawn


class Chess:
    def __init__(self):
        # Initialize board size and set the initial state
        self.board_row = 8
        self.board_col = 8
        self.start_pos = None
        self.turn = 'white'
        self.grid = None
        self.board = self.initialize_board()
        self.squares = [[None for _ in range(self.board_col)] for _ in range(self.board_row)]
        self.white_captured = []
        self.black_captured = []
        self.last_move = None
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
                                ui.image(image_path).style('pointer-events: none;')
                                # Allow clicks on the piece image
                                if isinstance(piece, King):
                                    self.add_king_context_menu(square, piece)
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

            if piece and (i, j) in piece.available_moves(self.board, self.last_move):
                # Check if piece is not None
                self.move_piece(start_row, start_col, i, j)
            else:
                ui.notify('Nieprawidłowy ruch!', color='red')
            self.start_pos = None


    def move_piece(self, start_row, start_col, end_row, end_col):
        piece = self.board[start_row][start_col]
        target_piece = self.board[end_row][end_col]

        # Is move is available
        if (end_row, end_col) not in piece.available_moves(self.board, self.last_move):
            ui.notify('Nieprawidłowy ruch!', color='red')
            return

        # If the piece is a King, ensure the move is safe
        if isinstance(piece, King):
            if not self.is_move_safe(start_row, start_col, end_row, end_col):
                ui.notify('Nie możesz wykonać tego ruchu, bo twój król będzie w szachu!', color='red')
                return

        # Simulate the move and check for check
        original_piece = self.board[end_row][end_col]
        original_x, original_y = piece.x, piece.y


        piece.x, piece.y = end_row, end_col
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None

        if self.isCheck(piece.color):
            # Cofnięcie symulacji
            self.board[start_row][start_col] = piece
            self.board[end_row][end_col] = original_piece
            piece.x, piece.y = original_x, original_y
            ui.notify('Nie możesz wykonać tego ruchu, bo twój król będzie w szachu!', color='red')
            return

        # Revert the move if it was safe
        self.board[start_row][start_col] = piece
        self.board[end_row][end_col] = original_piece
        piece.x, piece.y = original_x, original_y

        # Handle en passant capture
        if isinstance(piece, Pawn) and start_col != end_col and target_piece is None:
            captured_pawn = self.board[start_row][end_col]
            if isinstance(captured_pawn, Pawn) and captured_pawn.color != piece.color:
                self.board[start_row][end_col] = None
                if captured_pawn.color == 'white':
                    self.white_captured.append(captured_pawn)
                else:
                    self.black_captured.append(captured_pawn)
                self.update_square(start_row, end_col)

        # Normal capture
        elif target_piece:
            if target_piece.color == 'white':
                self.white_captured.append(target_piece)
            else:
                self.black_captured.append(target_piece)

        # Perform the move
        self.board[start_row][start_col] = None
        if isinstance(piece, Pawn):
            piece.move_piece(end_row, end_col, self.board)
        else:
            piece.move_piece(end_row, end_col)
        self.board[end_row][end_col] = piece

        # Update the board
        self.update_square(start_row, start_col)
        self.update_square(end_row, end_col)

        # Change turns
        self.turn = 'black' if self.turn == 'white' else 'white'

        # Check for check after the move
        if self.isCheck(self.turn):
            ui.notify(f'{self.turn.capitalize()} king is in check!', color='red')

        ui.notify(f'Przeniesiono {piece.__class__.__name__} na ({end_row}, {end_col})', color='blue')

        # Update captured pieces
        self.update_captured_pieces()

        self.last_move = (piece, (start_row, start_col), (end_row, end_col))

        # If the piece is a king, mark it as moved
        if isinstance(piece, King):
            piece.has_moved = True

    def add_king_context_menu(self, square, piece):
        with square:
            with ui.context_menu():
                ui.menu_item('Roszada długa', on_click=partial(self.handle_castling, piece, 'long'))
                ui.menu_item('Roszada krótka', on_click=partial(self.handle_castling, piece, 'short'))

    def handle_castling(self, piece, castling_type):
        if piece.color != self.turn:
            ui.notify('Ruch przeciwnika!', color='red')
            return

        start_row, start_col = piece.x, piece.y

        if piece.has_moved:
            ui.notify('Król już się ruszył, roszada niemożliwa!', color='red')
            return

        if castling_type == 'long':
            rook_col, end_col, rook_target_col = 0, 2, 3
        else:
            rook_col, end_col, rook_target_col = 7, 6, 5

        rook = self.board[start_row][rook_col]

        if not isinstance(rook, Rook) or rook.has_moved:
            ui.notify('Wieża już się ruszyła, roszada niemożliwa!', color='red')
            return

        if any(self.board[start_row][i] is not None for i in range(min(start_col, rook_col) + 1, max(start_col, rook_col))):
            ui.notify('Między królem a wieżą są figury, roszada niemożliwa!', color='red')
            return

        if self.is_check_on_castling_path(piece, start_row, start_col, end_col):
            ui.notify('Król jest w szachu lub przechodzi przez pole szachu, roszada niemożliwa!', color='red')
            return

        # Castling
        self.board[start_row][end_col] = piece
        self.board[start_row][start_col] = None
        self.board[start_row][rook_target_col] = rook
        self.board[start_row][rook_col] = None

        # Update position
        piece.x, piece.y = start_row, end_col
        rook.x, rook.y = start_row, rook_target_col


        piece.has_moved = True
        rook.has_moved = True

        # Update board
        self.update_square(start_row, start_col)
        self.update_square(start_row, end_col)
        self.update_square(start_row, rook_col)
        self.update_square(start_row, rook_target_col)

        self.turn = 'black' if self.turn == 'white' else 'white'


    def is_check_on_castling_path(self, piece, row, start_col, end_col):
        # Check if any squares the King would pass over (during castling) are attacked
        squares_to_check = []

        if start_col < end_col:
            squares_to_check = [(row, start_col), (row, start_col + 1), (row, start_col + 2)]
        else:
            squares_to_check = [(row, start_col), (row, start_col - 1), (row, start_col - 2), (row, start_col - 3)]

        # Simulate castling move to test if it puts the King in check
        temp_board = [r.copy() for r in self.board]
        temp_piece = temp_board[row][start_col]

        # Move the King
        temp_board[row][end_col] = temp_piece
        temp_board[row][start_col] = None

        # Move the Rook if short or long castling
        rook_col = 0 if start_col > end_col else 7
        rook_target_col = 3 if start_col > end_col else 5
        rook = temp_board[row][rook_col]
        temp_board[row][rook_target_col] = rook
        temp_board[row][rook_col] = None

        # Now check if any of the squares on the castling path or the King's new position are under attack
        for square in squares_to_check:
            if self.is_square_under_attack(square[0], square[1], temp_board):
                return True

        # Check the King's final position after castling
        if self.is_square_under_attack(row, end_col, temp_board):
            return True

        return False

    def is_square_under_attack(self, row, col, board=None):
        # Check if a given square is under attack by any opponent piece
        opponent_color = 'black' if self.turn == 'white' else 'white'

        # If no board is passed, use the current board state
        if board is None:
            board = self.board

        for r in board:
            for piece in r:
                if piece and piece.color == opponent_color:
                    if (row, col) in piece.available_moves(board, self.last_move):
                        return True
        return False


    def update_square(self, row, col):
        square = self.squares[row][col]
        square.clear()

        piece = self.board[row][col]
        if piece:
            piece_type = piece.__class__.__name__.lower()
            piece_color = piece.color
            image_path = f'./src/img/{piece_color}-pieces/{piece_type}-{piece_color}.png'

            with square:
                ui.image(image_path).style('pointer-events: none;')

    def update_captured_pieces(self):
        if not hasattr(self, 'captured_white_grid'):
            self.captured_white_grid = ui.grid(columns=4).classes('w-auto m-auto gap-0').style(
                'position: absolute; top: 50%; right: 0; transform: translateY(-50%); display: grid; grid-template-columns: repeat(4, 1fr); direction: rtl;'
            )
        if not hasattr(self, 'captured_black_grid'):
            self.captured_black_grid = ui.grid(columns=4).classes('w-auto m-auto gap-0').style(
                'position: absolute; top: 50%; left: 0; transform: translateY(-50%);'
            )

        self.captured_white_grid.clear()
        self.captured_black_grid.clear()

        with self.captured_white_grid:
            for piece in reversed(self.white_captured):
                with ui.element('div').style('width: 80px; height: 80px;').classes('m-auto'):
                    piece_type = piece.__class__.__name__.lower()
                    image_path = f'./src/img/white-pieces/{piece_type}-white.png'
                    ui.image(image_path)

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

        opponent_color = 'black' if color == 'white' else 'white'
        for row in self.board:
            for piece in row:
                if piece and piece.color == opponent_color:
                    if self.canSeeKing(king_pos, piece):
                        return True

        return False

    def canSeeKing(self, king_pos, piece):
        """
        Checks if a given piece can attack the king.
        :param king_pos: Position of the king (x, y)
        :param piece: The piece that may attack the king
        :return: True if the piece can attack the king, False otherwise
        """
        if not piece:
            return False

        # Check if the king's position is within the available moves of the piece
        if king_pos in piece.available_moves(self.board, self.last_move):
            return True

        # Additional check for pawns (special capture rules)
        if isinstance(piece, Pawn):
            direction = 1 if piece.color == 'white' else -1
            x, y = piece.x, piece.y
            # Check if the king is within the pawn's capture range
            if (king_pos == (x + direction, y - 1)) or (king_pos == (x + direction, y + 1)):
                return True

        return False

    def is_move_safe(self, start_row, start_col, end_row, end_col):
        """
        Simulates a move to check if it leaves the king in check.
        :param start_row: Starting row of the piece
        :param start_col: Starting column of the piece
        :param end_row: Ending row after the move
        :param end_col: Ending column after the move
        :return: True if the move is safe (king is not in check), False otherwise
        """
        piece = self.board[start_row][start_col]
        target_piece = self.board[end_row][end_col]

        # Save the original coordinates of the piece
        original_x, original_y = piece.x, piece.y

        # Simulate the move (update the board and piece coordinates)
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None
        piece.x, piece.y = end_row, end_col  # Update the coordinates of the piece

        # Check if the king is in check after the move
        is_safe = not self.isCheck(piece.color)

        # Undo the simulation (restore the board and piece coordinates)
        self.board[start_row][start_col] = piece
        self.board[end_row][end_col] = target_piece
        piece.x, piece.y = original_x, original_y  # Restore original coordinates

        return is_safe
