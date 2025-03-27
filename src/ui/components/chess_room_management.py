from src.services.game_state import GameStateService
from src.services.user_service import UserService
from nicegui import app, ui
import time


class ChessRoomManagement:
    def __init__(self, chess):
        self.game_state_service = GameStateService()
        self.chess = chess

    def check_for_updates(self):
        if self.chess.chess_timer.mode and self.chess.chess_timer.timer_running:
            self.chess.chess_timer.update_time(self.chess.turn)
            if self.chess.chess_timer.white_time <= 0:
                self.chess.end_game_class.end('black')
                self.chess.chess_timer.timer_running = False
                return
            if self.chess.chess_timer.black_time <= 0:
                self.chess.chess_timer.timer_running = False
                self.chess.end_game_class.end('white')
                return
        current_state = self.game_state_service.load_game_state(app.storage.user.get('game_state_id'))
        if not current_state and app.storage.user.get('game_state_id'):
            app.storage.user.update({'game_state_id': None, 'color': None})
            self.game_state_service.update_user_game_state(app.storage.user.get('user_id'), None, None)
            ui.notify('Nie znaleziono stanu gry!', color='red')
            ui.navigate.to('/')
            return
        if not current_state:
            return
        if current_state and current_state.get('timestamp', 0) > self.chess.last_update:
            self.load_game_state(app.storage.user.get('game_state_id'))
            self.chess.update_board()
            self.chess.update_captured_pieces()
            self.chess.last_update = current_state['timestamp']

    def load_game_state(self, game_state_id):
        """Load the game state from storage"""
        game_state = self.game_state_service.load_game_state(game_state_id)

        if not game_state and app.storage.user.get('game_state_id'):
            app.storage.user.update({'game_state_id': None, 'color': None})
            self.game_state_service.update_user_game_state(app.storage.user.get('user_id'), None, None)
            ui.notify('Nie znaleziono stanu gry!', color='red')
            ui.navigate.to('/')
            return
        # Load board state if it exists
        if game_state.get('board'):
            self.chess.board = self.deserialize_board(game_state['board'])

            # Load other game state properties
            self.chess.white_captured = self.deserialize_pieces(game_state.get('captured_white', []))
            self.chess.black_captured = self.deserialize_pieces(game_state.get('captured_black', []))
            self.chess.turn = game_state.get('turn', 'white')

            # Load last move if it exists
            if game_state.get('last_move'):
                piece_data, start_pos, end_pos = game_state['last_move']
                piece = self.deserialize_piece(piece_data)
                self.chess.last_move = (piece, start_pos, end_pos)
            else:
                self.chess.last_move = None
    def get_users(self, game_state_id):
        users = self.game_state_service.load_game_state(game_state_id)
        return users['users']

    def get_visitor(self, game_state_id):
        users = self.game_state_service.load_game_state(game_state_id)
        return users['visitors']


    def get_user_color(self, user_id):
        users = self.game_state_service.load_game_state(app.storage.user.get('game_state_id'))
        for user in users['users']:
            if user['id'] == user_id:
                return user['color']
        return None

    def save_game_state(self):
        """Save the current game state to storage"""
        if not app.storage.user.get('game_state_id'):
            return

        game_state = {
            'users': self.get_users(app.storage.user.get('game_state_id')),
            'visitors': self.get_visitor(app.storage.user.get('game_state_id')),
            'board': self.serialize_board(),
            'captured_white': self.serialize_pieces(self.chess.white_captured),
            'captured_black': self.serialize_pieces(self.chess.black_captured),
            'turn': self.chess.turn,
            'timestamp': time.time()
        }

        # Save last move if it exists
        if self.chess.last_move:
            piece, start_pos, end_pos = self.chess.last_move
            game_state['last_move'] = [self.serialize_piece(piece), start_pos, end_pos]
        else:
            game_state['last_move'] = None

        self.game_state_service.save_game_state(app.storage.user.get('game_state_id'), game_state)

    def serialize_board(self):
        """Convert the board to a serializable format"""
        serialized_board = []
        for row in range(self.chess.board_row):
            board_row = []
            for col in range(self.chess.board_col):
                piece = self.chess.board[row][col]
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
        board = [[None for _ in range(self.chess.board_col)] for _ in range(self.chess.board_row)]
        for row in range(self.chess.board_row):
            for col in range(self.chess.board_col):
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
            piece = piece_class(piece_data['color'], piece_data['x'], piece_data['y'], piece_data['has_moved'])
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