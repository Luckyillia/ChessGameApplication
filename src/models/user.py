class User:
    def __init__(self, user_id, name, surname, username, password, pesel, avatar):
        self.id = user_id
        self.name = name
        self.surname = surname
        self.username = username
        self.password = password
        self.pesel = pesel
        self.avatar = avatar

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "username": self.username,
            "password": self.password,
            "pesel": self.pesel,
            "avatar": self.avatar,
            "gameState": None
        }