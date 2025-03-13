import json
import os
import uuid
from src.models.user import User

class UserService:
    def __init__(self, file_name='data/data.json'):
        self.file_name = file_name

    def load_data(self):
        if not os.path.exists(self.file_name):
            return []
        try:
            with open(self.file_name, 'r', encoding='utf-8') as file:
                return json.load(file).get("users", [])
        except (json.JSONDecodeError, FileNotFoundError):
            print("❌ Błąd: Nie można wczytać danych z pliku JSON.")
            return []

    def write_data(self, users):
        try:
            with open(self.file_name, "w", encoding="utf-8") as outfile:
                json.dump(
                    {"users":  users},  # Konwersja do dict
                    outfile,
                    indent=4,
                    ensure_ascii=False
                )
        except Exception as e:
            print(f"❌ Błąd zapisu do pliku: {e}")

    def add_user(self, name, surname, pesel, avatar):
        users = self.load_data()
        user_id = str(uuid.uuid4())
        new_user = User(user_id, name, surname, pesel, avatar).to_dict()
        users.append(new_user)
        self.write_data(users)

    def delete_user(self, user_id):
        users = self.load_data()
        updated_users = [user for user in users if user['id'] != user_id]
        if len(updated_users) == len(users):
            return False
        self.write_data(updated_users)
        return True

    def edit_user(self, user_id, new_data):
        users = self.load_data()
        for user in users:
            if user['id'] == user_id:
                user.update(new_data)
                self.write_data(users)
                return True
        return False