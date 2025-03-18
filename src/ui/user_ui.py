from nicegui import app, ui
from src.ui.components.user_table import UserTable
from src.ui.components.user_chess import Chess
from src.services.registration import Registration
from src.services.user_service import UserService

class UserUI:
    def __init__(self):
        self.user_service = UserService()
        self.user_table = UserTable(self.user_service)
        self.setup_ui()


    def setup_ui(self):
        with ui.tabs().classes('w-full') as tabs:
            one = ui.tab('Dodaj użytkownika')
            two = ui.tab('Lista użytkowników')
            three = ui.tab('Szachy')

        ui.switch('Dark mode', on_change=self.switch)
        with ui.row().classes('w-full items-center px-4 py-2 rounded-lg'):
            ui.label(f'Witaj, {app.storage.user.get("username", "")}').classes(
                'text-xl font-semibold text-primary text-center flex-grow')
            ui.button(on_click=self.logout, icon='logout').props('outline round')
        with ui.tab_panels(tabs, value=one).classes('w-full flex justify-center items-center'):
            with ui.tab_panel(one):
                reg = Registration(self.user_table)

            with ui.tab_panel(two):
                self.user_table.init_table()

            with ui.tab_panel(three):
                chess = Chess()


    def switch(self, event):
        if event.value:
            ui.dark_mode().enable()
        else:
            ui.dark_mode().disable()

    def logout(self) -> None:
        app.storage.user.clear()
        ui.navigate.to('/login')