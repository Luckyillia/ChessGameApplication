from nicegui import ui
from src.services.user_service import UserService
from src.ui.components.user_table import UserTable
from src.ui.components.user_chess import Chess
import string
import random

class UserUI:
    def __init__(self):
        self.user_service = UserService()
        self.avatar_url = self.generate_avatar()
        self.setup_ui()

    def generate_avatar(self):
        chars = string.ascii_uppercase + string.digits
        return f'https://robohash.org/{"".join(random.choice(chars) for _ in range(5))}'

    def setup_ui(self):
        with ui.tabs().classes('w-full') as tabs:
            one = ui.tab('Dodaj użytkownika')
            two = ui.tab('Lista użytkowników')
            three = ui.tab('Szachy')

        ui.switch('Dark mode', on_change=self.switch)

        with ui.tab_panels(tabs, value=one).classes('w-full'):
            with ui.tab_panel(one):
                self.name_input = ui.input('Imię').classes('m-auto')
                self.surname_input = ui.input('Nazwisko').classes('m-auto')
                self.pesel_input = ui.input("PESEL").classes('m-auto')
                self.avatar_image = ui.image(self.avatar_url).classes('w-32 h-32').classes('m-auto')
                ui.button('Generuj nowy avatar', on_click=self.refresh_avatar).classes('m-auto')
                ui.button('Dodaj użytkownika', on_click=self.add_user).classes('m-auto')

            with ui.tab_panel(two):
                self.user_table = UserTable(self.user_service)

            with ui.tab_panel(three):
                chess = Chess()

    def add_user(self):
        if self.name_input.value and self.surname_input.value and self.pesel_input.value:
            if len(self.pesel_input.value) == 11 and self.pesel_input.value.isdigit():
                self.user_service.add_user(self.name_input.value, self.surname_input.value, self.pesel_input.value, self.avatar_url)
                self.name_input.value = ''
                self.surname_input.value = ''
                self.pesel_input.value = ''
                self.avatar_url = self.generate_avatar()
                self.avatar_image.set_source(self.avatar_url)
                self.user_table.update_table()
            else:
                ui.notify('PESEL musi zawierać 11 cyfr', color='red')
        else:
            ui.notify('Wszystkie pola muszą być wypełnione', color='red')

    def refresh_avatar(self):
        self.avatar_url = self.generate_avatar()
        self.avatar_image.set_source(self.avatar_url)

    def switch(self, event):
        if event.value:
            ui.dark_mode().enable()
        else:
            ui.dark_mode().disable()