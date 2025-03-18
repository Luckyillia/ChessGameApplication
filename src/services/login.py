from typing import Optional

from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.services.user_service import UserService
from src.services.registration import Registration

from nicegui import app, ui

# in reality users passwords would obviously need to be hashed

unrestricted_page_routes = {'/login', '/register'}


class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        if not app.storage.user.get('authenticated', False):
            if not request.url.path.startswith('/_nicegui') and request.url.path not in unrestricted_page_routes:
                return RedirectResponse(f'/login?redirect_to={request.url.path}')
        return await call_next(request)
@ui.page('/register')
def register() -> None:
    reg = Registration()

@ui.page('/login')
def login(redirect_to: str = '/') -> Optional[RedirectResponse]:
    def try_login() -> None:
        users = UserService().load_data()
        for user in users:
            if user['username'] == username.value and user['password'] == password.value:
                app.storage.user.update({'username': username.value, 'authenticated': True})
                ui.navigate.to(redirect_to)  # Powrót do żądanej strony
                return
        ui.notify('Wrong username or password', color='negative')

    if app.storage.user.get('authenticated', False):
        return RedirectResponse('/')

    with ui.card().classes('absolute-center'):
        username = ui.input('Username').on('keydown.enter', try_login)
        password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_login)
        ui.button('Log in', on_click=try_login)
        ui.button('Register', on_click=lambda: ui.navigate.to('/register'))

    return None

