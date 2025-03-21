from nicegui import ui
from functools import partial
from src.ui.components.chess_board import ChessBoard
from src.ui.components.chess_castling import ChessCastling
from src.ui.components.chess_endgame import ChessEndgame
from src.ui.components.chess_pieces import King, Pawn

class Chess:
    def __init__(self):
        # Initialize board size and set the initial state
        self.board_row = 8
        self.board_col = 8
        self.board_class = ChessBoard(self)
        self.end_game_class = ChessEndgame(self)
        self.handling_castling = ChessCastling(self)
        self.start_pos = None
        self.turn = 'white'
        self.grid = None
        self.board = self.board_class.init_stalemate()
        self.squares = [[None for _ in range(self.board_col)] for _ in range(self.board_row)]
        self.white_captured = []
        self.black_captured = []
        self.last_move = None
        self.create_chessboard()

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
                ui.notify(f'Selected piece at ({i}, {j})', color='blue')
            else:
                ui.notify('You cannot move this piece!', color='red')
        else:
            start_row, start_col = self.start_pos
            piece = self.board[start_row][start_col]

            if piece and (i, j) in piece.available_moves(self.board, self.last_move):
                # Check if piece is not None
                self.move_piece(start_row, start_col, i, j)
            else:
                ui.notify('Invalid move!', color='red')
            self.start_pos = None

    def move_piece(self, start_row, start_col, end_row, end_col):
        piece = self.board[start_row][start_col]
        target_piece = self.board[end_row][end_col]
        is_capture = False  # Flag to track captures

        # Check if the move is available
        if (end_row, end_col) not in piece.available_moves(self.board, self.last_move):
            ui.notify('Invalid move!', color='red')
            return

        # If the piece is a King, ensure the move is safe
        if isinstance(piece, King):
            if not self.end_game_class.is_move_safe(start_row, start_col, end_row, end_col):
                ui.notify('You cannot make this move because your king will be in check!', color='red')
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
            ui.notify('You cannot make this move because your king will be in check!', color='red')
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
        if self.end_game_class.isCheck(self.turn):
            if self.end_game_class.isCheckMate(self.turn):
                self.end_game_class.end('black' if self.turn == 'white' else 'white')
            else:
                ui.notify(f'{self.turn.capitalize()} king is in check!', color='red')
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

        # Notify about the moved piece
        ui.notify(f'Moved {piece.__class__.__name__} to ({end_row}, {end_col})', color='blue')

        # Update captured pieces
        self.update_captured_pieces()

        self.last_move = (piece, (start_row, start_col), (end_row, end_col))

        # If the piece is a King, mark it as moved
        if isinstance(piece, King):
            piece.has_moved = True

        # Check if it's a pawn move
        is_pawn_move = isinstance(piece, Pawn)
        # Update the move counter for the 75-move rule
        self.end_game_class.update_move_count(is_capture or is_pawn_move)

    def add_king_context_menu(self, square, piece):
        with square:
            with ui.context_menu():
                ui.menu_item('Long castling', on_click=partial(self.handling_castling.handle_castling, piece, 'long'))
                ui.menu_item('Short castling', on_click=partial(self.handling_castling.handle_castling, piece, 'short'))


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
                    image_path = f'./src/img/white-pieces/{piece_type}-white.png'
                    ui.image(image_path)

        with self.captured_black_grid:
            for piece in self.black_captured:
                with ui.element('div').style('width: 80px; height: 80px;').classes('m-auto'):
                    piece_type = piece.__class__.__name__.lower()
                    image_path = f'./src/img/black-pieces/{piece_type}-black.png'
                    ui.image(image_path)

    def update_board(self):
        for i in range(self.board_row):
            for j in range(self.board_col):
                self.update_square(i, j)