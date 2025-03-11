from nicegui import ui
import string
import random
import json
import os

file_name = 'data.json'
avatar_url = ""
dark = ui.dark_mode()

def load_data():
    if not os.path.exists(file_name):
        return []
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            return json.load(file).get("users", [])
    except (json.JSONDecodeError, FileNotFoundError):
        print("❌ Błąd: Nie można wczytać danych z pliku JSON.")
        return []

def write_data(users):
    try:
        with open(file_name, "w", encoding="utf-8") as outfile:
            json.dump({"users": users}, outfile, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Błąd zapisu do pliku: {e}")

# Generowanie losowego URL do avatara
def url_generator(size=5, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def generate_avatar():
    return f'https://robohash.org/{url_generator(5)}'

def add_user():
    global avatar_url
    users = load_data()
    if imie_input.value and nazwisko_input.value and pesel_input.value:
        if len(pesel_input.value) == 11 and pesel_input.value.isdigit():
            users.append({
                "name": imie_input.value,
                "surname": nazwisko_input.value,
                "pesel": pesel_input.value,
                "avatar": avatar_url
            })
            imie_input.value = ''
            nazwisko_input.value = ''
            pesel_input.value = ''
            avatar_url = generate_avatar()
            avatar_image.set_source(avatar_url)
            write_data(users)
            update_table()
        else:
            ui.notify('PESEL musi zawierać 11 cyfr', color='red')

def update_table():
    users = load_data()
    table.rows.clear()

    for user in users:
        table.rows.append({
            'name': user["name"],
            'surname': user["surname"],
            'pesel': user["pesel"],
            'avatar': user["avatar"]
        })
    table.update()

def switch(event):
    if event.value:
        dark.enable()
    else:
        dark.disable()

def refresh_avatar():
    global avatar_url
    avatar_url = generate_avatar()
    avatar_image.set_source(avatar_url)

# UI
with ui.tabs().classes('w-full') as tabs:
    one = ui.tab('Dodaj użytkownika')
    two = ui.tab('Lista użytkowników')

ui.switch('Dark mode', on_change=switch)

with ui.tab_panels(tabs, value=one).classes('w-full'):
    with ui.tab_panel(one):
        imie_input = ui.input('Imię')
        nazwisko_input = ui.input('Nazwisko')
        pesel_input = ui.input("PESEL")
        avatar_url = generate_avatar()
        avatar_image = ui.image(avatar_url).classes('w-24 h-24')
        ui.button('Generuj nowy avatar', on_click=refresh_avatar)
        ui.button('Dodaj użytkownika', on_click=add_user)

    with ui.tab_panel(two):
        columns = [
            {'name': 'name', 'label': 'Imię', 'field': 'name', 'align': 'left'},
            {'name': 'surname', 'label': 'Nazwisko', 'field': 'surname'},
            {'name': 'pesel', 'label': 'PESEL', 'field': 'pesel'},
            {'name': 'avatar', 'label': 'Avatar', 'field': 'avatar'},
        ]
        table = ui.table(columns=columns, rows=[], row_key='name',
                         column_defaults={'align': 'left', 'headerClasses': 'uppercase text-primary'}).classes('w-full')

        table.add_slot('body-cell-avatar', '''
        <q-td key="avatar" :props="props">
            <img :src="props.row.avatar" class="w-32 h-32 rounded-full">
        </q-td>
        ''')

        update_table()

ui.run()
