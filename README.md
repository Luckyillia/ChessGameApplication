# User Management System

This project is a simple user management system built using NiceGUI. It allows users to add new users with their details, including a randomly generated avatar, and view the list of added users. The system also supports dark mode.


## Installation

1. Clone the repository:
    ```bash
    git clone https://gitlab.makolab.net/interns/cc/niceguidemo
    cd NiceGUIdemo
    ```
3. Upgrade pip:
    ```bash
    python -m pip install --upgrade pip
    ```

3. Install the required dependencies:
    ```bash
    pip install nicegui
    ```

## Usage

1. Run the application:
    ```bash
    python test.py
    ```

2. Open your browser and navigate to `http://127.0.0.1:8080`.

## Code Overview

### `app.py`

This file contains the main logic of the application.

- **Imports**: Import necessary modules and libraries.
- **Global Variables**: Define global variables like `file_name` and `avatar_url`.
- **Functions**:
  - `load_data()`: Load user data from a JSON file.
  - `write_data(users)`: Write user data to a JSON file.
  - `url_generator(size, chars)`: Generate a random URL for avatars.
  - `generate_avatar()`: Generate a random avatar URL.
  - `add_user()`: Add a new user to the list.
  - `update_table()`: Update the user table with the latest data.
  - `switch(event)`: Toggle dark mode.
  - `refresh_avatar()`: Refresh the avatar image.
- **UI**:
  - Create tabs for adding users and viewing the user list.
  - Create input fields for user details.
  - Create buttons for generating avatars and adding users.
  - Create a table to display the list of users.

## Contact

Your Name - [@lucky_illia](https://www.instagram.com/lucky_ilIia/#) - zaichenko.illia@makolab.com

Project Link: [NiceGUIDemo](https://gitlab.makolab.net/interns/cc/niceguidemo)
