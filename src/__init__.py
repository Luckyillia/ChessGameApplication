# src/__init__.py

# Można tutaj dodać kod inicjalizujący cały pakiet, jeśli jest potrzebny.
# Na przykład zaimportować kluczowe moduły, aby były dostępne bezpośrednio z pakietu.

from .ui.user_ui import UserUI
from .services.user_service import UserService
from .models.user import User

__all__ = ['UserUI', 'UserService', 'User']  # Definiuje, co będzie dostępne przy imporcie z pakietu.