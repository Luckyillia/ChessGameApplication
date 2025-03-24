import json
import os
import uuid


class GameStateService:
    def __init__(self, file_name='data/game_state.json'):
        self.file_name = file_name
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        directory = os.path.dirname(self.file_name)
        if not os.path.exists(directory):
            os.makedirs(directory)

        if not os.path.exists(self.file_name):
            with open(self.file_name, 'w', encoding='utf-8') as file:
                json.dump({}, file)

    def load_game_state(self, game_state_id):
        """Load game state data for a specific ID"""
        try:
            with open(self.file_name, 'r', encoding='utf-8') as file:
                game_states = json.load(file)
                return game_states.get(game_state_id)
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"❌ Error: Could not load game state with ID {game_state_id}")
            return None

    def save_game_state(self, game_state_id, state_data):
        """Save game state data for a specific ID"""
        try:
            with open(self.file_name, 'r', encoding='utf-8') as file:
                try:
                    game_states = json.load(file)
                except json.JSONDecodeError:
                    game_states = {}

            game_states[game_state_id] = state_data

            temp_file_name = f"{self.file_name}.tmp"
            with open(temp_file_name, 'w', encoding='utf-8') as file:
                json.dump(game_states, file, indent=2)

            os.replace(temp_file_name, self.file_name)
            return True
        except Exception as e:
            print(f"❌ Error saving game state: {e}")
            return False

    def create_new_game_state(self):
        """Create a new empty game state and return its ID"""
        game_state_id = str(uuid.uuid4())
        empty_state = {
            "board": None,  # Will be initialized by the chess game
            "captured_white": [],
            "captured_black": [],
            "turn": "white",
            "last_move": None
        }
        self.save_game_state(game_state_id, empty_state)
        return game_state_id

    def update_user_game_state(self, user_id, game_state_id):
        """Update a user's game state ID in the user data"""
        from src.services.user_service import UserService
        user_service = UserService()
        users = user_service.load_data()

        for user in users:
            if user['id'] == user_id:
                user['gameState'] = game_state_id
                user_service.write_data(users)
                return True

        return False

    def get_file_modify(self):
        return os.path.getmtime(self.file_name)