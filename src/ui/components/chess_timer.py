from nicegui import ui


class ChessTimer:
    def __init__(self):
        self.white_time = 0  # in seconds
        self.black_time = 0  # in seconds
        self.timer_running = False
        self.mode = False  # False = no timer, True = timed game

        # Timer display elements
        self.white_display = ui.label('White: --:--').classes('text-xl font-bold mb-4')
        self.black_display = ui.label('Black: --:--').classes('text-xl font-bold mb-4')

        # Timer mode selection dialog
        self.mode_dialog = ui.dialog().classes('w-96')
        with self.mode_dialog, ui.card().classes('w-full gap-4 p-4'):
            ui.label('Wybierz tryb gry').classes('text-h6 text-center')
            self.white_time_input = ui.number('Czas dla białych (minuty)', value=5, min=1, max=60).classes('w-full')
            self.black_time_input = ui.number('Czas dla czarnych (minuty)', value=5, min=1, max=60).classes('w-full')
            ui.button('Graj z czasem', on_click=self.start_timed_game).classes('w-full')
            ui.button('Graj bez czasu', on_click=self.start_untimed_game).classes('w-full')

    def update_time(self, turn):
        if self.timer_running and self.mode:
            if turn == 'white':
                self.white_time -= 1
            elif turn == 'black':
                self.black_time -= 1

            # Update displays
            white_str, black_str = self.formated_time()
            self.white_display.text = f'White: {white_str}'
            self.black_display.text = f'Black: {black_str}'

            # Check for timeout
            if self.white_time <= 0:
                return 'black_wins'
            if self.black_time <= 0:
                return 'white_wins'
        return None

    def formated_time(self):
        """Format time as MM:SS"""
        white_time = f"{self.white_time // 60:02d}:{self.white_time % 60:02d}"
        black_time = f"{self.black_time // 60:02d}:{self.black_time % 60:02d}"
        return white_time, black_time

    def start_timed_game(self):
        """Start a new timed game"""
        self.white_time = int(self.white_time_input.value) * 60
        self.black_time = int(self.black_time_input.value) * 60
        self.mode = True
        self.mode_dialog.close()
        white_str, black_str = self.formated_time()
        self.white_display.text = f'White: {white_str}'
        self.black_display.text = f'Black: {black_str}'

    def start_untimed_game(self):
        """Start a game without timer"""
        self.mode = False
        self.timer_running = False
        self.mode_dialog.close()
        self.white_display.text = 'White: --:--'
        self.black_display.text = 'Black: --:--'

    def reset_timer(self):
        """Reset the timer to initial state"""
        self.timer_running = False
        self.white_time = 0
        self.black_time = 0
        self.white_display.text = 'White: --:--'
        self.black_display.text = 'Black: --:--'
