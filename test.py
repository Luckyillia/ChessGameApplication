from nicegui import events,ui
import string
import random
import json
import os

file_name = 'data.json'
avatar_url = ""

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
            user_id = str(len(users))  # Generate a simple unique ID based on the number of users
            users.append({
                "id": user_id,
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


def del_user(e: events.GenericEventArguments) -> None:
    print(f"🔹 Otrzymane argumenty: {e}")  # Debugowanie
    # Checking if event.args is a dictionary and retrieving user ID
    user_id = e.args.get('id') if isinstance(e.args, dict) else None
    if not user_id:
        print("❌ Błąd: ID użytkownika nie zostało przekazane!")
        ui.notify("❌ Błąd: ID użytkownika nie zostało przekazane!", color="red")  # Notify user of error
        return

    # Load user data and filter out the user with the provided ID
    users = load_data()
    updated_users = [user for user in users if user['id'] != user_id]  # Remove user with matching ID
    if len(updated_users) == len(users):
        print("❌ Błąd: Użytkownik nie został znaleziony!")
        ui.notify("❌ Błąd: Użytkownik nie został znaleziony!", color="red")
        return

    write_data(updated_users)  # Save the updated list of users
    update_table()  # Refresh the UI or data table
    ui.notify("✅ Użytkownik usunięty!", color="green")  # Success notification


def update_table():
    users = load_data()
    table.rows.clear()

    for user in users:
        table.rows.append({
            'name': user["name"],
            'surname': user["surname"],
            'pesel': user["pesel"],
            'avatar': user["avatar"],
            'id': user['id']
        })
    table.update()

def switch(event):
    print(event)
    if event.value:
        ui.dark_mode().enable()
        print('dark')
    else:
        ui.dark_mode().disable()
        print('white')

def refresh_avatar():
    global avatar_url
    avatar_url = generate_avatar()
    avatar_image.set_source(avatar_url)

# UI
with ui.tabs().classes('w-full') as tabs:
    one = ui.tab('Dodaj użytkownika')
    two = ui.tab('Lista użytkowników')
    three = ui.tab('Szachy')

ui.switch('Dark mode', on_change=switch)

with ui.tab_panels(tabs, value=one).classes('w-full'):
    with ui.tab_panel(one):
        imie_input = ui.input('Imię').classes('m-auto')
        nazwisko_input = ui.input('Nazwisko').classes('m-auto')
        pesel_input = ui.input("PESEL").classes('m-auto')
        avatar_url = generate_avatar()
        avatar_image = ui.image(avatar_url).classes('w-32 h-32').classes('m-auto')
        ui.button('Generuj nowy avatar', on_click=refresh_avatar).classes('m-auto')
        ui.button('Dodaj użytkownika', on_click=add_user).classes('m-auto')

    with ui.tab_panel(two):
        columns = [
            {'name': 'name', 'label': 'Imię', 'field': 'name', 'align': 'center'},
            {'name': 'surname', 'label': 'Nazwisko', 'field': 'surname', 'align': 'center'},
            {'name': 'pesel', 'label': 'PESEL', 'field': 'pesel', 'align': 'center'},
            {'name': 'avatar', 'label': 'Avatar', 'field': 'avatar', 'align': 'center'},
            {'name': 'id', 'label': 'Akcja', 'field': 'id', 'align': 'center'},  # Kolumna akcji
        ]
        table = ui.table(columns=columns, rows=[], row_key='id',
                         column_defaults={'align': 'center', 'headerClasses': 'uppercase text-primary', 'justify-content' : 'center'}).classes('w-full')

        table.add_slot('body-cell-avatar', '''
        <q-td key="avatar" :props="props" class="text-center">
            <div class="flex justify-center">
                <img :src="props.row.avatar" class="w-52 h-52 rounded-full">
            </div>
        </q-td> 
        ''')

        table.add_slot('body-cell-id', '''
        <q-td key="id" class="text-center">
            <div class="flex justify-center items-center gap-2">
                <q-btn color="red" dense icon="delete" 
                    @click="() => $parent.$emit('delete', props.row)">Usuń</q-btn>
                <q-btn color="primary" dense icon="edit"
                    @click="() => $parent.$emit('edit', props.row)">Edytuj</q-btn>
            </div>
        </q-td>
        ''')
        update_table()
    with ui.tab_panel(three):
        ui.label('Test')
table.on('delete', del_user)
table.on('edit', del_user)
ui.run()