from src.ui.components.chess_pieces import *
from src.ui.components.chess_board import * 


class ChessEndgame:
    def __init__(self, chess):
        self.chess = chess
        self.chess_board = ChessBoard(self.chess)
        
    def isCheck(self, color):
        """
        Sprawdza, czy król danego koloru jest w szachu.
        :param color: Kolor króla ('white' lub 'black')
        :return: True, jeśli król jest w szachu, False w przeciwnym razie
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
        Sprawdza, czy król danego koloru jest zamatowany.
        :param color: Kolor króla ('white' lub 'black')
        :return: True, jeśli mat, False w przeciwnym razie
        """
        # Sprawdź, czy król jest w szachu
        if not self.isCheck(color):
            return False

        # Iteruj przez wszystkie figury gracza
        for row in range(self.chess.board_row):
            for col in range(self.chess.board_col):
                piece = self.chess.board[row][col]
                if piece and piece.color == color:
                    # Pobierz wszystkie dostępne ruchy dla figury
                    moves = piece.available_moves(self.chess.board, self.chess.last_move)
                    for (new_row, new_col) in moves:
                        # Symuluj ruch i sprawdź, czy król jest bezpieczny
                        if self.is_move_safe(row, col, new_row, new_col):
                            return False  # Znaleziono ruch, który usuwa szacha

        return True  # Brak możliwych ruchów — mat

    def isStalemate(self, color):
        """
        Sprawdza, czy wystąpił pat.
        :param color: Kolor gracza, który ma wykonać ruch ('white' lub 'black')
        :return: True, jeśli pat, False w przeciwnym razie
        """
        # Sprawdź, czy król nie jest w szachu
        if self.isCheck(color):
            return False

        # Iteruj przez wszystkie figury gracza
        for row in range(self.chess.board_row):
            for col in range(self.chess.board_col):
                piece = self.chess.board[row][col]
                if piece and piece.color == color:
                    # Pobierz wszystkie dostępne ruchy dla figury
                    moves = piece.available_moves(self.chess.board, self.chess.last_move)
                    for (new_row, new_col) in moves:
                        # Symuluj ruch i sprawdź, czy król jest bezpieczny
                        if self.is_move_safe(row, col, new_row, new_col):
                            return False  # Znaleziono legalny ruch

        return True  # Brak możliwych ruchów — pat

    def end(self, color=None):
        def restart_game():
            self.chess.board = self.chess_board.init_board()
            self.chess.turn = 'white'
            self.chess.last_move = None
            self.chess.white_captured = []
            self.chess.black_captured = []
            self.chess.update_captured_pieces()
            self.chess.update_board()
            dialog.close()

        with ui.dialog() as dialog, ui.card().classes('p-4'):
            if color:
                ui.label(f'{color.capitalize()} Won').classes('text-xl font-bold text-center w-full')
            else:
                ui.label('Draw').classes('text-xl font-bold text-center w-full')
            
            with ui.row().classes('justify-center w-full'):
                ui.button('Restartuj Grę', on_click=restart_game).classes(
                    'bg-green-500 text-white hover:bg-green-700 focus:outline-none focus:ring-4 focus:ring-green-500'
                )
                ui.button('Zobacz planszę', on_click=dialog.close).classes(
                    'bg-green-500 text-white hover:bg-green-700 focus:outline-none focus:ring-4 focus:ring-green-500'
                )

        dialog.open()