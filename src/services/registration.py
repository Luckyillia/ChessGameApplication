from nicegui import ui
from src.services.user_service import UserService
import random, string

from src.ui.components import user_table


class Registration:
    def __init__(self, user_table = None):
        self.user_service = UserService()
        self.user_table = user_table
        self.avatar_url = self.generate_avatar()
        self.name_input = ui.input('Imię').classes('m-auto w-64')
        self.surname_input = ui.input('Nazwisko').classes('m-auto w-64')
        self.username_input = ui.input('Username').classes('m-auto w-64')
        self.password_input = ui.input('Password', password=True, password_toggle_button=True).classes('m-auto w-64')
        self.pesel_input = ui.input("PESEL").classes('m-auto w-64')
        self.avatar_image = ui.image(self.avatar_url).classes('w-32 h-32 m-auto')
        ui.button('Generuj nowy avatar', on_click=self.refresh_avatar).classes('m-auto w-64')
        ui.button('Dodaj użytkownika', on_click=self.add_user).classes('m-auto w-64')
        if not self.user_table:
            ui.button('Wroc', on_click=lambda: ui.navigate.to('/login')).classes('m-auto w-64')


    def generate_avatar(self):
        chars = string.ascii_uppercase + string.digits
        return f'https://robohash.org/{"".join(random.choice(chars) for _ in range(5))}'

    def refresh_avatar(self):
        self.avatar_url = self.generate_avatar()
        self.avatar_image.set_source(self.avatar_url)

    def add_user(self, redirect_to: str = '/'):
        if self.name_input.value and self.surname_input.value and self.pesel_input.value:
            if len(self.pesel_input.value) == 11 and self.pesel_input.value.isdigit():
                self.user_service.add_user(self.name_input.value, self.surname_input.value, self.username_input.value, self.password_input.value, self.pesel_input.value, self.avatar_url)
                self.name_input.value = ''
                self.surname_input.value = ''
                self.username_input.value = ''
                self.password_input.value = ''
                self.pesel_input.value = ''
                self.avatar_url = self.generate_avatar()
                self.avatar_image.set_source(self.avatar_url)
                if self.user_table:
                    self.user_table.update_table()
                else:
                    ui.navigate.to(redirect_to)

            else:
                ui.notify('PESEL musi zawierać 11 cyfr', color='red')
        else:
            ui.notify('Wszystkie pola muszą być wypełnione', color='red')