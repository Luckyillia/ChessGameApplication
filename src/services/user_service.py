import json
import os
import uuid
from src.models.user import User


class UserService:
    def __init__(self, file_name='data/data.json'):
        # Initialize file name for data storage
        self.file_name = file_name

    def load_data(self):
        # Ensure the directory exists
        directory = os.path.dirname(self.file_name)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Return empty list if file doesn't exist or is empty
        if not os.path.exists(self.file_name):
            return []
        if os.stat(self.file_name).st_size == 0:
            return []

        # Try to load the JSON data
        try:
            with open(self.file_name, 'r', encoding='utf-8') as file:
                return json.load(file).get("users", [])
        except (json.JSONDecodeError, FileNotFoundError):
            print("❌ Error: Could not load data from JSON file.")
            return []

    def write_data(self, users):
        # Write data to the file
        try:
            directory = os.path.dirname(self.file_name)
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Convert data to JSON format
            data_to_write = json.dumps(
                {"users": users},  # Convert data to dict
                indent=4,
                ensure_ascii=False
            )

            # Write to a temporary file and then replace the original file
            temp_file_name = f"{self.file_name}.tmp"
            with open(temp_file_name, "w", encoding="utf-8") as temp_file:
                temp_file.write(data_to_write)

            os.replace(temp_file_name, self.file_name)

        except Exception as e:
            print(f"❌ Error writing to file: {e}")

    def add_user(self, name, surname, username, password, pesel, avatar):
        # Add a new user to the system
        users = self.load_data()
        for user in users:
            if user['username'] == username:
                return False
        user_id = str(uuid.uuid4())
        new_user = User(user_id, name, surname, username, password, pesel, avatar).to_dict()
        users.append(new_user)
        self.write_data(users)
        return True

    def delete_user(self, user_id):
        # Delete a user by ID
        users = self.load_data()
        updated_users = [user for user in users if user['id'] != user_id]
        if len(updated_users) == len(users):
            return False
        self.write_data(updated_users)
        return True

    def edit_user(self, user_id, new_data):
        # Edit a user's details by ID
        users = self.load_data()
        for user in users:
            if user['id'] == user_id:
                user.update(new_data)
                self.write_data(users)
                return True
        return False
