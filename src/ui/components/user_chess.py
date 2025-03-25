from nicegui import app, ui
from functools import partial

from src.ui.components.chess_board import ChessBoard
from src.ui.components.chess_castling import ChessCastling
from src.ui.components.chess_endgame import ChessEndgame
from src.ui.components.chess_pieces import King, Pawn
from src.services.game_state import GameStateService
from src.ui.components.chess_room_management import ChessRoomManagement


class Chess:
    def __init__(self):
        # Initialize board size and set the initial state
        self.board_row = 8
        self.board_col = 8

        self.game_state_service = GameStateService()
        self.board_class = ChessBoard()
        self.end_game_class = ChessEndgame(self)
        self.handling_castling = ChessCastling(self)
        self.chess_room_management = ChessRoomManagement(self)

        self.start_pos = None
        self.turn = 'white'
        self.grid = None
        self.board = [[None for _ in range(self.board_col)] for _ in range(self.board_row)]
        self.squares = [[None for _ in range(self.board_col)] for _ in range(self.board_row)]
        self.white_captured = []
        self.black_captured = []
        self.last_move = None
        self.last_update = 0

        # Try to load saved game state
        if app.storage.user.get('game_state_id'):
            self.chess_room_management.load_game_state(app.storage.user.get('game_state_id'))

        self.create_chessboard()

        self.PIECE_NAMES_PL = {
            "Pawn": "Pionek",
            "Rook": "Wieża",
            "Knight": "Skoczek",
            "Bishop": "Goniec",
            "Queen": "Królowa",
            "King": "Król",
        }
        self.TURN_PL = {
            "black": "Czarnych",
            "white": "Białych"
        }

        ui.timer(interval=1.0, callback=self.chess_room_management.check_for_updates)

    def create_chessboard(self):
        if app.storage.user.get('game_state_id') is None:
            room_dialog = ui.dialog().classes('w-full')
            with room_dialog, ui.card():
                ui.label('Brak aktywnego pokoju gry').classes('text-center text-xl font-bold')
                ui.label('Utwórz nowy pokój poprzez menu aplikacji').classes('text-center')
                ui.button('Zamknij', on_click=lambda: room_dialog.close())
            room_dialog.open()

        self.grid = ui.grid(columns=8).classes('w-auto m-auto gap-0')

        # Create chessboard
        with self.grid:
            for i in range(self.board_row):
                for j in range(self.board_col):
                    # Estimate background color
                    color = '#769656' if (i + j) % 2 == 0 else '#EEEED2'
                    # Estimate text color
                    text_color = '#EEEED2' if color == '#769656' else '#769656'

                    # Calculate reversed row number (8 at the top, 1 at the bottom)
                    reversed_row = self.board_row - i  # Reverse the order of rows (8 -> 1)

                    # Make the background div non-interactive
                    with ui.element('div').style(
                            f'background-color: {color}; width: 100px; height: 100px; position: relative;').on(
                        'click', partial(self.handle_square_click, i, j)) as square:

                        # Add the label with the column letter first and then the reversed row number
                        ui.label(f'{chr(ord("a") + j)}{reversed_row}').style(
                            f'position: absolute; top: 2px; right: 2px; font-size: 10px; color: {text_color};')

                        self.squares[i][j] = square
                        if app.storage.user.get('game_state_id') is not None:
                            piece = self.board[i][j]
                            if piece:
                                piece_type = piece.__class__.__name__.lower()
                                piece_color = piece.color
                                # Updated image path to match your directory structure
                                image_path = f'./src/img/{piece_color}-pieces/{piece_type}-{piece_color}.png'

                                # Make the chess pieces interactive
                                with square:
                                    ui.image(image_path).style('pointer-events: none;')
                                    # Allow clicks on the piece image
                                    if isinstance(piece, King):
                                        self.add_king_context_menu(square, piece)
        self.update_captured_pieces()

    def handle_square_click(self, i, j):
        # [Existing code remains the same]
        piece = self.board[i][j]
        piece_name_pl = self.PIECE_NAMES_PL.get(piece.__class__.__name__, piece.__class__.__name__) if piece else None
        if self.start_pos is None:
            if piece and self.turn == piece.color:
                self.start_pos = (i, j)
                ui.notify(f'Wybrano {piece_name_pl}', color='blue')
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
        # [Existing code with save_game_state added at the end]
        piece = self.board[start_row][start_col]
        target_piece = self.board[end_row][end_col]
        is_capture = False  # Flag to track captures
        piece_name_pl = self.PIECE_NAMES_PL.get(piece.__class__.__name__, piece.__class__.__name__)
        turn_pl = self.TURN_PL.get(self.turn, self.turn)

        if app.storage.user.get('color') != self.turn:
            ui.notify('Nie twoja kolej!', color='red')
            return

        # Check if the move is available
        if (end_row, end_col) not in piece.available_moves(self.board, self.last_move):
            ui.notify('Nieprawidłowy ruch!', color='red')
            return

        # If the piece is a King, ensure the move is safe
        if isinstance(piece, King):
            if not self.end_game_class.is_move_safe(start_row, start_col, end_row, end_col):
                ui.notify('Nie możesz wykonać tego ruchu, bo twój król będzie w szachu!', color='red')
                return

        # Simulate the move and check for check
        original_piece = self.board[end_row][end_col]
        original_x, original_y = piece.x, piece.y

        piece.x, piece.y = end_row, end_col
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None

        if self.end_game_class.isCheck(piece.color):
            # Undo the simulation
            self.board[start_row][start_col] = piece
            self.board[end_row][end_col] = original_piece
            piece.x, piece.y = original_x, original_y
            ui.notify('Nie możesz wykonać tego ruchu, bo twój król będzie w szachu!', color='red')
            return

        # Restore the move if it was safe
        self.board[start_row][start_col] = piece
        self.board[end_row][end_col] = original_piece
        piece.x, piece.y = original_x, original_y

        # Handle en passant capture
        if isinstance(piece, Pawn) and start_col != end_col and target_piece is None:
            captured_pawn = self.board[start_row][end_col]
            if isinstance(captured_pawn, Pawn) and captured_pawn.color != piece.color:
                is_capture = True  # Mark en passant capture
                self.board[start_row][end_col] = None
                if captured_pawn.color == 'white':
                    self.white_captured.append(captured_pawn)
                else:
                    self.black_captured.append(captured_pawn)
                self.update_square(start_row, end_col)

        # Normal capture
        elif target_piece:
            is_capture = True  # Mark normal capture
            if target_piece.color == 'white':
                self.white_captured.append(target_piece)
            else:
                self.black_captured.append(target_piece)

        # Perform the move
        self.board[start_row][start_col] = None
        if isinstance(piece, Pawn):
            piece.move_piece(end_row, end_col, self)
        else:
            piece.move_piece(end_row, end_col)
        self.board[end_row][end_col] = piece

        # Update the board
        self.update_square(start_row, start_col)
        self.update_square(end_row, end_col)

        # Change turns
        self.turn = 'black' if self.turn == 'white' else 'white'

        # Check check after move
        if self.end_game_class.isCheck(self.turn):
            if self.end_game_class.isCheckMate(self.turn):
                self.end_game_class.end('black' if self.turn == 'white' else 'white')
            else:
                piece_name = self.PIECE_NAMES_PL["King"]  # Get the name for "King"
                turn_name = self.TURN_PL[self.turn]  # Get the name for the turn ("Białych" or "Czarnych")
                ui.notify(f'{turn_name} {piece_name} jest w szachu!', color='red')


        else:
            # Check for stalemate
            if self.end_game_class.isStalemate(self.turn):
                self.end_game_class.end()  # Assume the `end` method handles a draw
            elif self.end_game_class.is_king_vs_king():
                self.end_game_class.end()  # Assume the `end` method handles a draw
            elif self.end_game_class.is_75_move_rule():
                self.end_game_class.end()  # Assume the `end` method handles a draw
            else:
                pass

        # Notification after move piece
        notation = f'{chr(ord("a") + end_col)}{8 - end_row}'
        ui.notify(f'Przeniesiono {piece_name_pl} na {notation}', color='blue')

        # Update captured pieces
        self.update_captured_pieces()

        self.last_move = (piece, (start_row, start_col), (end_row, end_col))

        # If the piece is a king, mark it as moved
        if isinstance(piece, King):
            piece.has_moved = True

        # Check if it's a pawn move
        is_pawn_move = isinstance(piece, Pawn)
        # Update the move counter for the 75-move rule
        self.end_game_class.update_move_count(is_capture or is_pawn_move)

        # Save game state after move
        self.chess_room_management.save_game_state()

    # [Rest of the methods remain the same]
    def add_king_context_menu(self, square, piece):
        with square:
            with ui.context_menu():
                ui.menu_item('Roszada długa', on_click=partial(self.handling_castling.handle_castling, piece, 'long'))
                ui.menu_item('Roszada krótka', on_click=partial(self.handling_castling.handle_castling, piece, 'short'))

    def update_square(self, row, col):
        square = self.squares[row][col]
        square.clear()

        # Calculate reversed row number (8 at the top, 1 at the bottom)
        reversed_row = self.board_row - row  # Reverse the order of rows (8 -> 1)

        # Recreating the numbering of the fields
        color = '#769656' if (row + col) % 2 == 0 else '#EEEED2'
        text_color = '#EEEED2' if color == '#769656' else '#769656'
        with square:
            ui.label(f'{chr(ord("a") + col)}{reversed_row}').style(
                f'position: absolute; top: 2px; right: 2px; font-size: 10px; color: {text_color};')

        piece = self.board[row][col]
        if piece:
            piece_type = piece.__class__.__name__.lower()
            piece_color = piece.color
            # Updated image path to match your directory structure
            image_path = f'./src/img/{piece_color}-pieces/{piece_type}-{piece_color}.png'

            with square:
                ui.image(image_path).style('pointer-events: none;')
                if isinstance(piece, King):
                    self.add_king_context_menu(square, piece)

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
                    # Updated image path to match your directory structure
                    image_path = f'./src/img/white-pieces/{piece_type}-white.png'
                    ui.image(image_path)

        with self.captured_black_grid:
            for piece in self.black_captured:
                with ui.element('div').style('width: 80px; height: 80px;').classes('m-auto'):
                    piece_type = piece.__class__.__name__.lower()
                    # Updated image path to match your directory structure
                    image_path = f'./src/img/black-pieces/{piece_type}-black.png'
                    ui.image(image_path)

    def update_board(self):
        for i in range(self.board_row):
            for j in range(self.board_col):
                self.update_square(i, j)