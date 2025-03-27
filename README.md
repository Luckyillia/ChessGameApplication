# Chess Game Application

The **Chess Game Application** is an advanced Python project focused on creating an interactive chess-playing experience. The application combines user management features (such as registration, login, and account maintenance) with a fully functional chess game. It is built using the `nicegui` library for a user-friendly interface and incorporates many advanced chess mechanics to ensure robust gameplay.

---

## Features

### 1. **User Management**
- Registration of new users with required fields like name, surname, username, password, and PESEL.
- Automatic generation of user avatars using RoboHash, with an option to refresh the avatar.
- Login system that authenticates users and manages session states.
- A user table for administrators with options to add, edit, or delete users.

### 2. **Chess Gameplay**
- Full implementation of chess rules, including:
  - King castling (both short and long).
  - En passant pawn capture.
  - Pawn promotion.
  - Check, checkmate, and stalemate detection.
- Interactive chessboard where pieces can be moved via drag-and-drop while validating legal moves.
- Various endgame conditions (e.g., 75-move rule, insufficient material, king vs. king).

### 3. **Game Management**
- Creation and management of chess rooms for multiplayer gameplay.
- Synchronization of game states between participants in a chess room (e.g., active user turn and piece placement).
- Saving and loading chess games for continued gameplay.

### 4. **Secure Data Handling**
- User and game data are securely managed and stored locally in JSON files.
- Username validation to prevent duplicates.
- PESEL validation to ensure correct input (11 digits).

### 5. **Modern UI**
- Responsive and user-friendly interface using the `nicegui` library.
- Toggleable dark mode.
- Easy navigation with streamlined workflows for both admins and players.

### 6. ChessBoard Module

The `chess_board.py` module is the backbone of the game's chessboard functionality. It manages the creation, initialization, and resetting of the chessboard, as well as setting up specific game scenarios. Key features of this module include:

- **Initialization of the Chessboard:** Sets up a standard chessboard with pieces in their starting positions.
- **Key Gameplay Scenarios:**
  - **Castling (Short and Long):** Implements the logic for enabling both types of castling.
  - **En Passant:** Handles the logic for capturing pawns using the en passant rule.
  - **Pawn Promotion:** Manages the promotion of pawns upon reaching the opposite end of the board.
  - **Check and Checkmate Detection:** Provides methods for identifying checks and potential checkmate situations.
  - **Stalemate Detection:** Checks for scenarios where a stalemate occurs.
- **Custom Game Scenarios:**
  - Allows for the creation of specific chessboard configurations, such as `king_vs_king` or empty chessboards for testing or custom setups.

This module is crucial for ensuring realistic chess gameplay and contributes to simulating all possible game states according to the official rules of chess.

---

## Project Structure
```text
ChessGame/
│
├── 📂 data
│   ├── 📄 data.json
│   └── 📄 game_state.json
├── 📂 doc
│   ├── 📄 ArchitectureClasses.drawio
│   └── 📄 Coding Standard - Python.pdf
├── 📄 README.md
├── 📄 requirements.txt
├── 📂 src
│   ├── 📂 img
│   │   ├── 📂 black-pieces
│   │   │   ├── 📄 bishop-black.png
│   │   │   ├── 📄 king-black.png
│   │   │   ├── 📄 knight-black.png
│   │   │   ├── 📄 pawn-black.png
│   │   │   ├── 📄 queen-black.png
│   │   │   └── 📄 rook-black.png
│   │   └── 📂 white-pieces
│   │       ├── 📄 bishop-white.png
│   │       ├── 📄 king-white.png
│   │       ├── 📄 knight-white.png
│   │       ├── 📄 pawn-white.png
│   │       ├── 📄 queen-white.png
│   │       └── 📄 rook-white.png
│   ├── 📄 main.py
│   ├── 📂 models
│   │   ├── 📄 user.py
│   │   └── 📄 __init__.py
│   │
│   ├── 📂 services
│   │   ├── 📄 game_state.py
│   │   ├── 📄 login.py
│   │   ├── 📄 registration.py
│   │   ├── 📄 user_service.py
│   │   └──📄 __init__.py
│   │
│   ├── 📂 ui
│   │   ├── 📂 components
│   │   │   ├── 📄 chess_board.py
│   │   │   ├── 📄 chess_castling.py
│   │   │   ├── 📄 chess_endgame.py
│   │   │   ├── 📄 chess_pieces.py
│   │   │   ├── 📄 chess_room_management.py
│   │   │   ├── 📄 user_chess.py
│   │   │   ├── 📄 user_table.py
│   │   │   └── 📄 __init__.py
│   │   │ 
│   │   ├── 📄 user_ui.py
│   │   └── 📄 __init__.py
│   │   
│   └──📄 __init__.py
│   
└── 📄 test.py
```
---
## Statystyki Kodowania w Projekcie

```text
┏━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━┓
┃ Language    ┃ Files ┃     % ┃ Code ┃     % ┃ Comment ┃   % ┃
┡━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━┩
│ Python      │    20 │  52.6 │ 1543 │  69.7 │     203 │ 9.2 │
│ Markdown    │     1 │   2.6 │  152 │  70.7 │       0 │ 0.0 │
│ Text only   │     1 │   2.6 │   59 │ 100.0 │       0 │ 0.0 │
│ JSON        │     2 │   5.3 │   55 │  77.5 │       0 │ 0.0 │
│ __unknown__ │     1 │   2.6 │    0 │   0.0 │       0 │ 0.0 │
│ __binary__  │    13 │  34.2 │    0 │   0.0 │       0 │ 0.0 │
├─────────────┼───────┼───────┼──────┼───────┼─────────┼─────┤
│ Sum         │    38 │ 100.0 │ 1809 │  70.7 │     203 │ 7.9 │
└─────────────┴───────┴───────┴──────┴───────┴─────────┴─────┘
```

---

## Installation and Setup

### Prerequisites
- Python 3.12 or later.

### Installation Steps
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd chess-game-application
   ```

2. (Optional) Create a virtual environment to isolate dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/MacOS
   .\.venv\Scripts\activate   # Windows
   ```

3. Upgrade pip:
   ```bash
   python -m pip install --upgrade pip
   ```

4. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the application:
   ```bash
   python -m src.main
   ```

6. Open the application in your web browser at:
   ```
   http://localhost:8080
   ```

---

## Usage

### 1. Registration and Login
- Create a new user account via the registration page.
- Login to access the main dashboard with features like creating a new chess game.

### 2. Chess Gameplay
- Create or join a chess room to start a game.
- Play against other users (or as a visitor) by moving pieces on the board.
- Follow the game rules, and the system will check for valid moves, captures, and game-ending conditions.

### 3. User Management
- Admins can use the user table interface to view, add, edit, or delete user accounts.
- Update avatars or regenerate them dynamically.

---

## Technologies Used

- **Python** – Core application logic.
- **NiceGUI** – Modern and reactive front-end library for GUIs in Python.
- **JSON** – Storage for user data and game states.
- **FastAPI** – Middleware for authentication and routing requests.

---

## Data Structure

The app stores user information in a JSON file (`data/data.json`).

**Example user data:**
```json
{
    "users": [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Jan",
            "surname": "Kowalski",
            "username": "janek",
            "password": "password123",
            "pesel": "12345678901",
            "avatar": "https://robohash.org/ABCDE",
            "gameState": null,
            "color": null
        }
    ]
}
```

The app stores game information in a JSON file (`data/game_state.json`).

**Example user game_state:**
```json
{
  "a1e5cd94-94f6-4c74-b4b8-5c54d7353b9b": {
    "users": [
      "84ed04e0-69a0-40c5-92f4-f8904118369a"
    ],
    "visitors": [
      "84ed04e0-69a0-40c5-92f4-f8904118369a"
    ],
    "board": [],
    "captured_white": [],
    "captured_black": [],
    "turn": "black",
    "timestamp": 1743002166.8977764,
    "last_move": [
      {
        "type": "Queen",
        "color": "white",
        "x": 1,
        "y": 3,
        "has_moved": false,
        "first_move": false
      },
      [
        1,
        4
      ],
      [
        1,
        3
      ]
    ]
  }
}
```
---

## Contribution Guidelines

We welcome contributions from the community! Feel free to:
- Report bugs.
- Suggest new features or improvements.
- Submit pull requests to enhance functionality or optimize code.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.

---

## Authors

**Authors:**
- **Illia Zaichenko** – *Original creator* – [zaichemko.illia](https://gitlab.makolab.net/zaichenko.illia)
- **Maximilian Kuster** – *Original creator* – [kuster.maximilian](https://gitlab.makolab.net/kuster.maximilian)

If you have any questions or suggestions, feel free to reach out! 🚀 