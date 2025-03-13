class User:
    def __init__(self, user_id, name, surname, pesel, avatar):
        self.id = user_id
        self.name = name
        self.surname = surname
        self.pesel = pesel
        self.avatar = avatar

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "pesel": self.pesel,
            "avatar": self.avatar
        }