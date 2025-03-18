from nicegui import app, ui
from src.services.login import AuthMiddleware
from src.ui.user_ui import UserUI
from src.services.registration import Registration

if __name__ in {"__main__", "__mp_main__"}:
    # registration = Registration()
    app.add_middleware(AuthMiddleware)


    @ui.page('/')
    def main_page() -> None:
        user_ui = UserUI()

    ui.run(storage_secret='THIS_NEEDS_TO_BE_CHANGED')