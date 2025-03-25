import uuid

from nicegui import app, ui
from src.ui.components.user_table import UserTable
from src.ui.components.user_chess import Chess
from src.services.registration import Registration
from src.services.user_service import UserService
from src.services.game_state import GameStateService
from src.ui.components.chess_board import ChessBoard


class UserUI:
    def __init__(self):
        # Initialize user service and user table
        self.user_service = UserService()
        self.game_state_service = GameStateService()
        self.user_table = UserTable(self.user_service)
        self.setup_ui()

    def setup_ui(self):
        # Create UI tabs
        with ui.tabs().classes('w-full') as tabs:
            one = ui.tab('Dodaj użytkownika')
            two = ui.tab('Lista użytkowników')
            three = ui.tab('Szachy')

        self.room_dialog = ui.dialog().classes('w-full')
        with self.room_dialog, ui.card():
            self.room_code_label = ui.label().classes('text-xl font-bold')
            ui.button("Zamknij", on_click=self.room_dialog.close).classes('m-2')

        self.join_dialog = ui.dialog().classes('w-full')
        with self.join_dialog, ui.card():
            ui.label('Dołącz do pokoju').classes('text-xl font-bold')
            self.room_code_input = ui.input(label='Kod pokoju').classes('w-full')
            with ui.row().classes('w-full justify-end'):
                ui.button('Anuluj', on_click=self.join_dialog.close).classes('m-2')
                ui.button('Dołącz', on_click=self.handle_join).classes('m-2')

        # User info and logout button
        with ui.row().classes('w-full items-center px-4 py-2 rounded-lg flex justify-center'):
            ui.switch('Dark mode', on_change=self.switch).classes(' flex-grow')
            result = ui.label().classes('mr-auto')
            ui.label(f'Witaj, {app.storage.user.get("username", "")}').classes(
                'text-xl font-semibold text-primary text-center')
            ui.button(on_click=self.logout, icon='logout').props('outline round')
            with ui.button(icon='menu').props('outline round'):
                with ui.menu() as menu:
                    ui.menu_item('Utwórz nowy pokój', lambda: (self.create_new_room(), menu.close()))
                    ui.menu_item('Wyjdź z pokoju', lambda: (self.exit_room(), menu.close()))
                    ui.menu_item('Dołącz do pokoju', lambda: (self.join_room(), menu.close()))
                    ui.menu_item('Sprawdz kod pokoju', lambda: (self.check_room_id(), menu.close()))
                    ui.separator()
                    ui.menu_item('Close', menu.close)

        # Define content for each tab
        with ui.tab_panels(tabs, value=one).classes('w-full flex justify-center items-center'):
            with ui.tab_panel(one):
                reg = Registration(self.user_table)

            with ui.tab_panel(two):
                self.user_table.init_table()

            with ui.tab_panel(three):
                self.chess = Chess()

    def switch(self, event):
        # Toggle dark mode based on switch
        if event.value:
            ui.dark_mode().enable()
        else:
            ui.dark_mode().disable()

    def logout(self) -> None:
        # Clear user session and navigate to login page
        app.storage.user.clear()
        ui.navigate.to('/login')

    def create_new_room(self):
        if not app.storage.user.get('game_state_id'):
            game_state_id = self.game_state_service.create_new_game_state(app.storage.user.get('user_id'))
            self.game_state_service.update_user_game_state(app.storage.user.get('user_id'), game_state_id , 'white')
            app.storage.user.update({'game_state_id': game_state_id, 'color': 'white'})
            self.chess.board = ChessBoard().init_board()
            self.chess.update_board()
            self.chess.chess_room_management.save_game_state()
            self.room_code_label.text = f'Kod pokoju: {game_state_id}'
            ui.update()  # Wymuś aktualizację interfejsu
            self.room_dialog.open()
        else:
            ui.notify('You are already in a room')

    def exit_room(self):
        game_state_id = app.storage.user.get('game_state_id')
        app.storage.user.update({'game_state_id': None, 'color': None})
        self.game_state_service.update_user_game_state(app.storage.user.get('user_id'), None, None)
        self.game_state_service.delete_game_state(game_state_id)
        ui.notify('You have exited the room')
        ui.navigate.to('/')
     

    def join_room(self):
        if app.storage.user.get('game_state_id'):
            ui.notify('Już jesteś w pokoju!', type='warning')
            return
        self.room_code_input.set_value(None)
        self.join_dialog.open()

    def handle_join(self):
        try:
            room_code = self.room_code_input.value.strip()
            if not room_code:
                raise ValueError('Pole nie może być puste')

            # Walidacja formatu UUID
            if not self.validate_uuid(room_code):
                raise ValueError('Nieprawidłowy format kodu')

            # Sprawdzenie istnienia pokoju
            if not self.game_state_service.game_state_exists(room_code):
                raise ValueError('Pokój nie istnieje')

            # Aktualizacja stanu użytkownika
            if not self.game_state_service.add_user_to_game_state(room_code,app.storage.user.get('user_id')):
                raise ValueError('Pokój jest przepelniony')
            app.storage.user.update({'game_state_id': room_code, 'color': 'black'})

            self.game_state_service.update_user_game_state(app.storage.user.get('user_id'), room_code, 'black')

            # Inicjalizacja szachów
            self.chess.chess_room_management.load_game_state(room_code)
            self.chess.update_board()

            ui.notify('Pomyślnie dołączono do pokoju!', type='positive')
            self.join_dialog.close()

        except ValueError as e:
            ui.notify(str(e), type='negative')
        except Exception as e:
            ui.notify(f'Błąd: {str(e)}', type='negative')
            print(f'Error joining room: {e}')

    @staticmethod
    def validate_uuid(value: str) -> bool:
        try:
            uuid.UUID(value)
            return True
        except ValueError:
            return False

    def check_room_id(self):
        self.room_code_label.text = f'Kod pokoju: {app.storage.user.get("game_state_id")}'
        ui.update()
        self.room_dialog.open()
