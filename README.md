# User Management System

The **User Management System** is a Python-based application that allows managing users, including adding, editing, and deleting their data, as well as generating random avatars. The application uses the `nicegui` library to create a user-friendly interface designed for simplicity and ease of use.



---

## Installation

### This project require Python 3.12

1. Clone the repository:
   ```bash
   git clone https://gitlab.makolab.net/interns/cc/niceguidemo
   cd NiceGUIdemo
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/MacOS
   .\.venv\Scripts\activate   # Windows
   ```

3. Upgrade pip:
   ```bash
   python.exe -m pip install --upgrade pip
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the application:
   ```bash
   python -m src.main
   ```

---

## Project Structure

```
NiceGUIdemo/
│
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── user_service.py
│   └── ui/
│       ├── __init__.py
│       ├── user_ui.py
│       └── components/
│           ├── __init__.py
│           └── user_table.py
│
├── data/
│   └── data.json
│
└── requirements.txt
```

---

## Usage

1. **Adding a User**:
    - Navigate to the "Add User" tab.
    - Fill in the required fields: `First Name`, `Last Name`, and `PESEL`.
    - Click "Add User" to save the data.

2. **Viewing Users**:
    - Go to the "User List" tab to see the list of registered users.

3. **Editing a User**:
    - In the "User List" tab, select a user and update their details.

4. **Deleting a User**:
    - In the "User List" tab, choose a user and remove them from the database.

5. **Generating a New Avatar**:
    - In the "Add User" tab, click "Generate New Avatar" to get a unique avatar.

6. **Switching Dark Mode**:
    - Use the "Dark Mode" toggle to switch between light and dark themes.

---

## Technologies

- **Python** – Backend logic.
- **NiceGUI** – User interface development.
- **JSON** – Local storage for user data.

---

## Sample Data Structure

The application stores user data in a JSON file (`data/data.json`). Example data structure:

```json
{
    "users": [
        {
            "id": "e7aa07c8-9982-45f5-b1c4-713a5dde317e",
            "name": "Anna",
            "surname": "Nowak",
            "pesel": "12345678901",
            "avatar": "https://robohash.org/ABCDEF"
        }
    ]
}
```

---

## Contributions

We welcome contributions to improve the project! Feel free to report bugs, suggest new features, or submit Pull Requests.

---

## License

This project is licensed under the MIT License. Details can be found in the `LICENSE` file.

---

## Authors

- **Illia Zaichenko** – *Original creator* – [zaichemko.illia](https://gitlab.makolab.net/zaichenko.illia)
- **Maximilian Kuster** – *Original creator* – [kuster.maximilian](https://gitlab.makolab.net/kuster.maximilian)

If you have any questions or suggestions, feel free to reach out! 🚀