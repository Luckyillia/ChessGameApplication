from nicegui import ui
from src.ui.components.chess_pieces import *

class ChessCastling:
    def __init__(self, chess):
        self.chess = chess

    def handle_castling(self, piece, castling_type):
        if piece.color != self.chess.turn:
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

        rook = self.chess.board[start_row][rook_col]

        if not isinstance(rook, Rook) or rook.has_moved:
            ui.notify('Wieża już się ruszyła, roszada niemożliwa!', color='red')
            return

        if any(self.chess.board[start_row][i] is not None for i in range(min(start_col, rook_col) + 1, max(start_col, rook_col))):
            ui.notify('Między królem a wieżą są figury, roszada niemożliwa!', color='red')
            return

        if self.is_check_on_castling_path(piece, start_row, start_col, end_col):
            ui.notify('Król jest w szachu lub przechodzi przez pole szachu, roszada niemożliwa!', color='red')
            return

        # Castling
        self.chess.board[start_row][end_col] = piece
        self.chess.board[start_row][start_col] = None
        self.chess.board[start_row][rook_target_col] = rook
        self.chess.board[start_row][rook_col] = None

        # Update position
        piece.x, piece.y = start_row, end_col
        rook.x, rook.y = start_row, rook_target_col


        piece.has_moved = True
        rook.has_moved = True

        # Update board
        self.chess.update_square(start_row, start_col)
        self.chess.update_square(start_row, end_col)
        self.chess.update_square(start_row, rook_col)
        self.chess.update_square(start_row, rook_target_col)

        self.chess.turn = 'black' if self.chess.turn == 'white' else 'white'


    def is_check_on_castling_path(self, piece, row, start_col, end_col):
        # Check if any squares the King would pass over (during castling) are attacked
        squares_to_check = []

        if start_col < end_col:
            squares_to_check = [(row, start_col), (row, start_col + 1), (row, start_col + 2)]
        else:
            squares_to_check = [(row, start_col), (row, start_col - 1), (row, start_col - 2), (row, start_col - 3)]

        # Simulate castling move to test if it puts the King in check
        temp_board = [r.copy() for r in self.chess.board]
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
        opponent_color = 'black' if self.chess.turn == 'white' else 'white'

        # If no board is passed, use the current board state
        if board is None:
            board = self.chess.board

        for r in board:
            for piece in r:
                if piece and piece.color == opponent_color:
                    if (row, col) in piece.available_moves(board, self.chess.last_move):
                        return True
        return False