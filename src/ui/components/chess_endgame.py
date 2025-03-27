from src.ui.components.chess_pieces import *
from src.ui.components.chess_board import *
from nicegui import ui, app
from src.services.game_state import GameStateService
from src.ui.components.chess_room_management import ChessRoomManagement

class ChessEndgame:
    def __init__(self, chess):
        self.chess = chess
        self.chess_board = ChessBoard()
        self.chess_room_management = ChessRoomManagement(self.chess)
        self.move_count_since_last_capture_or_pawn_move = 0  # Counter for the 50-move rule

    def isCheck(self, color):
        """
        Checks if the king of the given color is in check.
        :param color: Color of the king ('white' or 'black')
        :return: True if the king is in check, False otherwise
        """
        king_pos = None
        for row in self.chess.board:
            for piece in row:
                if isinstance(piece, King) and piece.color == color:
                    king_pos = (piece.x, piece.y)
                    break
            if king_pos:
                break

        if not king_pos:
            return False

        opponent_color = 'black' if color == 'white' else 'white'
        for row in self.chess.board:
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
        if king_pos in piece.available_moves(self.chess.board, self.chess.last_move):
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
        piece = self.chess.board[start_row][start_col]
        target_piece = self.chess.board[end_row][end_col]

        # Save the original coordinates of the piece
        original_x, original_y = piece.x, piece.y

        # Simulate the move (update the board and piece coordinates)
        self.chess.board[end_row][end_col] = piece
        self.chess.board[start_row][start_col] = None
        piece.x, piece.y = end_row, end_col  # Update the coordinates of the piece

        # Check if the king is in check after the move
        is_safe = not self.isCheck(piece.color)

        # Undo the simulation (restore the board and piece coordinates)
        self.chess.board[start_row][start_col] = piece
        self.chess.board[end_row][end_col] = target_piece
        piece.x, piece.y = original_x, original_y  # Restore original coordinates
        piece.x, piece.y = original_x, original_y

        return is_safe

    def isCheckMate(self, color):
        """
        Checks if the king of the given color is checkmated.
        :param color: Color of the king ('white' or 'black')
        :return: True if checkmate, False otherwise
        """
        # Check if the king is in check
        if not self.isCheck(color):
            return False

        # Iterate through all pieces of the player
        for row in range(self.chess.board_row):
            for col in range(self.chess.board_col):
                piece = self.chess.board[row][col]
                if piece and piece.color == color:
                    # Get all available moves for the piece
                    moves = piece.available_moves(self.chess.board, self.chess.last_move)
                    for (new_row, new_col) in moves:
                        # Simulate the move and check if the king is safe
                        if self.is_move_safe(row, col, new_row, new_col):
                            return False  # Found a move that removes the check

        return True  # No possible moves — checkmate

    def isStalemate(self, color):
        """
        Checks if a stalemate has occurred.
        :param color: Color of the player whose turn it is ('white' or 'black')
        :return: True if stalemate, False otherwise
        """
        # Check if the king is not in check
        if self.isCheck(color):
            return False

        # Iterate through all pieces of the player
        for row in range(self.chess.board_row):
            for col in range(self.chess.board_col):
                piece = self.chess.board[row][col]
                if piece and piece.color == color:
                    # Get all available moves for the piece
                    moves = piece.available_moves(self.chess.board, self.chess.last_move)
                    for (new_row, new_col) in moves:
                        # Simulate the move and check if the king is safe
                        if self.is_move_safe(row, col, new_row, new_col):
                            return False  # Found a legal move

        return True  # No possible moves — stalemate

    def is_king_vs_king(self):
        """
        Checks if only kings are left on the board.
        :return: True if only kings remain, False otherwise
        """
        for row in self.chess.board:
            for piece in row:
                if piece and not isinstance(piece, King):
                    return False
        return True

    def is_75_move_rule(self):
        """
        Checks if the 75-move rule applies.
        :return: True if 150 half-moves (75 full moves) have passed without a capture or pawn move
        """
        return self.move_count_since_last_capture_or_pawn_move >= 150


    def update_move_count(self, reset_counter):
        """
        Updates the move counter for the 75-move rule.
        :param reset_counter: True if the move was a capture or pawn move
        """
        if reset_counter:
            self.move_count_since_last_capture_or_pawn_move = 0
        else:
            self.move_count_since_last_capture_or_pawn_move += 1



    def end(self, color=None):
        def restart_game():
            game_state_id = app.storage.user.get('game_state_id')
            self.chess.last_move = None
            self.chess.white_captured = []
            self.chess.black_captured = []
            self.move_count_since_last_capture_or_pawn_move = 0
            GameStateService().restart_game_state(game_state_id, self.chess_room_management, self.chess)
            self.chess.board = ChessBoard().init_board()
            self.chess.update_board()
            self.chess_room_management.save_game_state()
            dialog.close()

        with ui.dialog() as dialog, ui.card().classes('p-4'):
            if color:
                ui.label(f'{color.capitalize()} Won').classes('text-xl font-bold text-center w-full')
            else:
                ui.label('Draw').classes('text-xl font-bold text-center w-full')

            with ui.row().classes('justify-center w-full'):
                ui.button('Restartuj Gre', on_click=restart_game).classes(
                    'bg-green-500 text-white hover:bg-green-700 focus:outline-none focus:ring-4 focus:ring-green-500'
                )
                ui.button('Zobacz plansze', on_click=dialog.close).classes(
                    'bg-green-500 text-white hover:bg-green-700 focus:outline-none focus:ring-4 focus:ring-green-500'
                )
        self.chess.chess_timer.timer_running = False
        dialog.open()