from typing import Optional

from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.services.user_service import UserService
from src.services.registration import Registration
from src.services.game_state import GameStateService

from nicegui import app, ui

# In reality, user passwords would need to be hashed for security reasons

UNRESTRICTED_PAGE_ROUTES = {'/login', '/register'}


class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        # Check if the user is authenticated
        if not app.storage.user.get('authenticated', False):
            # Redirect to login if the user is not authenticated and trying to access restricted pages
            if not request.url.path.startswith('/_nicegui') and request.url.path not in UNRESTRICTED_PAGE_ROUTES:
                return RedirectResponse(f'/login?redirect_to={request.url.path}')
        return await call_next(request)


@ui.page('/register')
def register() -> None:
    reg = Registration()


@ui.page('/login')
def login(redirect_to: str = '/') -> Optional[RedirectResponse]:
    def try_login() -> None:
        # Load user data
        users = UserService().load_data()
        for user in users:
            # Check if the provided username and password match a user
            if user['username'] == username.value and user['password'] == password.value:
                # Check if user has a game state
                game_state_id = user.get('gameState')
                if not game_state_id:
                    # Create a new game state if none exists
                    game_state_service = GameStateService()
                    game_state_id = game_state_service.create_new_game_state()
                    game_state_service.update_user_game_state(user['id'], game_state_id)

                # Mark user as authenticated and store game state ID
                app.storage.user.update({
                    'username': username.value,
                    'user_id': user['id'],
                    'authenticated': True,
                    'game_state_id': game_state_id
                })
                ui.navigate.to(redirect_to)
                return
        # Notify user if the login failed
        ui.notify('Wrong username or password', color='negative')

    # If the user is already authenticated, redirect to the home page
    if app.storage.user.get('authenticated', False):
        return RedirectResponse('/')

    # Render the login page
    with ui.card().classes('absolute-center'):
        username = ui.input('Username').on('keydown.enter', try_login)
        password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_login)
        ui.button('Log in', on_click=try_login)
        ui.button('Register', on_click=lambda: ui.navigate.to('/register'))

    return None