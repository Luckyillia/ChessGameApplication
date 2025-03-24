from nicegui import app, ui
from functools import partial
from src.ui.components.chess_board import ChessBoard
from src.ui.components.chess_castling import ChessCastling
from src.ui.components.chess_endgame import ChessEndgame
from src.ui.components.chess_pieces import King, Pawn
from src.services.game_state import GameStateService



class Chess:
    def __init__(self):
        # Initialize board size and set the initial state
        self.board_row = 8
        self.board_col = 8
        self.game_state_service = GameStateService()

        # Load game state if available
        self.game_state_id = app.storage.user.get('game_state_id')

        self.board_class = ChessBoard()
        self.end_game_class = ChessEndgame(self)
        self.handling_castling = ChessCastling(self)
        self.start_pos = None
        self.turn = 'white'
        self.grid = None
        self.squares = [[None for _ in range(self.board_col)] for _ in range(self.board_row)]
        self.white_captured = []
        self.black_captured = []
        self.last_move = None

        # Try to load saved game state
        if self.game_state_id:
            self.load_game_state()
        else:
            # Initialize a new board if no state is found
            self.board = self.board_class.init_board()
            self.save_game_state()  # Save the initial state

        self.create_chessboard()

        self.last_update = 0
        ui.timer(interval=1.0, callback=self.check_for_updates)


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
    def check_for_updates(self):
        current_timestamp = self.game_state_service.get_file_modify()

        if current_timestamp > self.last_update:
            self.load_game_state()
            self.update_board()
            self.update_captured_pieces()
            self.last_update = current_timestamp

    def load_game_state(self):
        """Load the game state from storage"""
        game_state = self.game_state_service.load_game_state(self.game_state_id)

        if not game_state:
            # If no game state is found, initialize a new board
            self.board = self.board_class.init_board()
            return

        # Load board state if it exists
        if game_state.get('board') is None:
            self.board = self.board_class.init_board()
        else:
            # Deserialize the board from the saved state
            self.board = self.deserialize_board(game_state['board'])

        # Load other game state properties
        self.white_captured = self.deserialize_pieces(game_state.get('captured_white', []))
        self.black_captured = self.deserialize_pieces(game_state.get('captured_black', []))
        self.turn = game_state.get('turn', 'white')

        # Load last move if it exists
        if game_state.get('last_move'):
            piece_data, start_pos, end_pos = game_state['last_move']
            piece = self.deserialize_piece(piece_data)
            self.last_move = (piece, start_pos, end_pos)
        else:
            self.last_move = None

    def save_game_state(self):
        """Save the current game state to storage"""
        if not self.game_state_id:
            return

        game_state = {
            'board': self.serialize_board(),
            'captured_white': self.serialize_pieces(self.white_captured),
            'captured_black': self.serialize_pieces(self.black_captured),
            'turn': self.turn,
        }

        # Save last move if it exists
        if self.last_move:
            piece, start_pos, end_pos = self.last_move
            game_state['last_move'] = [self.serialize_piece(piece), start_pos, end_pos]
        else:
            game_state['last_move'] = None

        self.game_state_service.save_game_state(self.game_state_id, game_state)

    def serialize_board(self):
        """Convert the board to a serializable format"""
        serialized_board = []
        for row in range(self.board_row):
            board_row = []
            for col in range(self.board_col):
                piece = self.board[row][col]
                if piece:
                    board_row.append(self.serialize_piece(piece))
                else:
                    board_row.append(None)
            serialized_board.append(board_row)
        return serialized_board

    def serialize_piece(self, piece):
        """Convert a piece to a serializable format"""
        if not piece:
            return None

        return {
            'type': piece.__class__.__name__,
            'color': piece.color,
            'x': piece.x,
            'y': piece.y,
            'has_moved': getattr(piece, 'has_moved', False),
            'first_move': getattr(piece, 'first_move', False)
        }

    def serialize_pieces(self, pieces):
        """Convert a list of pieces to a serializable format"""
        return [self.serialize_piece(piece) for piece in pieces]

    def deserialize_board(self, board_data):
        """Convert serialized board data back to a board with piece objects"""
        board = [[None for _ in range(self.board_col)] for _ in range(self.board_row)]
        for row in range(self.board_row):
            for col in range(self.board_col):
                if board_data[row][col]:
                    board[row][col] = self.deserialize_piece(board_data[row][col])
        return board

    def deserialize_piece(self, piece_data):
        """Convert serialized piece data back to a piece object"""
        if not piece_data:
            return None

        # Import all piece classes
        from src.ui.components.chess_pieces import Pawn, Rook, Knight, Bishop, Queen, King

        # Map piece type names to classes
        piece_classes = {
            'Pawn': Pawn,
            'Rook': Rook,
            'Knight': Knight,
            'Bishop': Bishop,
            'Queen': Queen,
            'King': King
        }

        # Create the piece object
        piece_class = piece_classes.get(piece_data['type'])
        if not piece_class:
            return None
        if isinstance(piece_class, Pawn):
            piece = piece_class(piece_data['color'], piece_data['x'], piece_data['y'])
        else:
            piece = piece_class(piece_data['color'], piece_data['x'], piece_data['y'])

        # Set additional properties
        if 'has_moved' in piece_data:
            piece.has_moved = piece_data['has_moved']
        if 'first_move' in piece_data:
            piece.first_move = piece_data['first_move']

        return piece

    def deserialize_pieces(self, pieces_data):
        """Convert serialized pieces data back to piece objects"""
        return [self.deserialize_piece(piece_data) for piece_data in pieces_data]

    def create_chessboard(self):
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
            piece.move_piece(end_row, end_col, self.board, self)
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
        self.save_game_state()

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