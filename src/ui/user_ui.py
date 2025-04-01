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
        self.menu = None
        self.chess = None
        self.setup_ui()

    def setup_ui(self):
        # Create UI tabs
        with ui.tabs().classes('w-full') as tabs:
            one = ui.tab('Dodaj użytkownika')
            two = ui.tab('Lista użytkowników')
            three = ui.tab('Szachy')
            four = ui.tab('Profile')

        self.room_dialog = ui.dialog().classes('w-full')
        with self.room_dialog, ui.card():
            self.room_code_label = ui.label().classes('text-xl font-bold')
            ui.button("Zamknij", on_click=self.room_dialog.close).classes('m-2')
            ui.button('Skopiuj do schowka', on_click=lambda: [ui.clipboard.write(app.storage.user.get('game_state_id')),
                                                                   ui.notify('Skopiowano do schowku', color='positive', icon='inventory')])

        self.join_dialog = ui.dialog().classes('w-full')
        with self.join_dialog, ui.card():
            ui.label('Dołącz do pokoju').classes('text-xl font-bold')
            self.room_code_input = ui.input(label='Kod pokoju').classes('w-full')
            with ui.row().classes('w-full justify-end'):
                ui.button('Anuluj', on_click=self.join_dialog.close).classes('m-2')
                ui.button('Wklej', on_click=self.handle_paste).classes('m-2')
                ui.button('Dołącz', on_click=self.handle_join).classes('m-2')
            ui.button('Dołącz jako widz', on_click=self.visitor_join).classes('m-2')

        # User info and logout button
        with ui.row().classes('w-full items-center px-4 py-2 rounded-lg flex justify-center'):
            ui.switch('Dark mode', on_change=self.switch).classes(' flex-grow')
            result = ui.label().classes('mr-auto')
            ui.label(f'Witaj, {app.storage.user.get("username", "")}').classes(
                'text-xl font-semibold text-primary text-center')
            ui.button(on_click=self.logout, icon='logout').props('outline round')
            with ui.button(icon='menu').props('outline round'):
                self.menu = ui.menu().classes('w-64')
                with self.menu:
                    ui.menu_item('Utwórz nowy pokój', lambda: (self.create_new_room(), self.menu.close()))
                    ui.menu_item('Wyjdź z pokoju', lambda: (self.exit_room(), self.menu.close()))
                    ui.menu_item('Dołącz do pokoju', lambda: (self.join_room(), self.menu.close()))
                    ui.menu_item('Sprawdz kod pokoju', lambda: (self.check_room_id(), self.menu.close()))
                    ui.separator()
                    ui.menu_item('Close', self.menu.close)

        self.chess = Chess(self.menu)

        # Define content for each tab
        with ui.tab_panels(tabs, value=one).classes('w-full flex justify-center items-center'):
            with ui.tab_panel(one):
                reg = Registration(self.user_table)

            with ui.tab_panel(two):
                if app.storage.user.get('username') == 'lucky_illia' or app.storage.user.get('username') == 'Yojson':
                    self.user_table.init_table()
                else:
                    ui.notify('Nie masz uprawnien', color='red')

            with ui.tab_panel(three):
                self.chess.create_chessboard()

            with ui.tab_panel(four):
                with ui.card().classes('m-auto'):
                    user = self.user_service.get_user(app.storage.user.get('user_id'))
                    ui.label('Profile').classes('text-xl font-semibold text-primary text-center m-auto')
                
                    ui.label(f'Imie: {user['name']}').classes('text-xl font-semibold text-primary text-center m-auto')
                    name = ui.input('Imie', visible='False')
                    ui.label(f'Nazwisko: {user['surname']}').classes('text-xl font-semibold text-primary text-center m-auto')
                    ui.label(f'Nazwa uzytkownika: {user['username']}').classes('text-xl font-semibold text-primary text-center m-auto')
                    ui.image(user['avatar']).classes('w-32 h-32 m-auto')

    async def handle_paste(self):
        code = await ui.clipboard.read()
        self.room_code_input.set_value(code)
        ui.notify('Wklejono ze schowka', color='positive', icon='content_paste')

    def switch(self, event):
        # Toggle dark mode based on switch
        if event.value:
            ui.dark_mode().enable()
        else:
            ui.dark_mode().disable()

    def logout(self) -> None:
        # Clear user session and navigate to login page
        self.exit_room()
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
            ui.update()
            self.chess.chess_timer.mode_dialog.open()
        else:
            ui.notify('Juz jestes w pokoju!', type='warning')

    def exit_room(self):
        if not app.storage.user.get('game_state_id'):
            ui.notify('Nie jestes w zadnym pokoju!', type='warning')
            return
        game_state_id = app.storage.user.get('game_state_id')
        color = app.storage.user.get('color')
        if color is None and game_state_id is not None:
            app.storage.user.update({'game_state_id': None, 'color': None})
            self.game_state_service.update_user_game_state(app.storage.user.get('user_id'), None, None)
            self.game_state_service.delete_visitor_id(game_state_id ,app.storage.user.get('user_id'))
        else:
            app.storage.user.update({'game_state_id': None, 'color': None})
            self.game_state_service.update_user_game_state(app.storage.user.get('user_id'), None, None)
            self.game_state_service.delete_game_state(game_state_id)
        ui.notify('Wyszedles z pokoju!', type='positive')
        ui.navigate.to('/')
     

    def join_room(self):
        if app.storage.user.get('game_state_id'):
            ui.notify('Już jesteś w pokoju!', type='warning')
            return
        self.room_code_input.set_value(None)
        self.join_dialog.open()

    def visitor_join(self):
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
            if not self.game_state_service.add_visitor_to_game_state(room_code,app.storage.user.get('user_id')):
                raise ValueError('Cos poszlo nie tak')
            app.storage.user.update({'game_state_id': room_code, 'color': None})
            self.game_state_service.update_user_game_state(app.storage.user.get('user_id'), room_code, None)

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
