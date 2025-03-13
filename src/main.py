from nicegui import ui
from src.ui.user_ui import UserUI

if __name__ in {"__main__", "__mp_main__"}:
    user_ui = UserUI()
    ui.run()