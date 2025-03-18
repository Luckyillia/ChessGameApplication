from nicegui import ui, events
from src.services.user_service import UserService

class UserTable:
    def __init__(self, user_service: UserService):
        self.user_service = user_service


    def init_table(self):
        self.columns = [
            {'name': 'name', 'label': 'Imię', 'field': 'name', 'align': 'center'},
            {'name': 'surname', 'label': 'Nazwisko', 'field': 'surname', 'align': 'center'},
            {'name': 'username', 'label': 'Username', 'field': 'username', 'align': 'center'},
            {'name': 'password', 'label': 'Haslo', 'field': 'password', 'align': 'center'},
            {'name': 'pesel', 'label': 'PESEL', 'field': 'pesel', 'align': 'center'},
            {'name': 'avatar', 'label': 'Avatar', 'field': 'avatar', 'align': 'center'},
            {'name': 'id', 'label': 'Akcja', 'field': 'id', 'align': 'center'},
        ]
        self.table = ui.table(columns=self.columns, rows=[], row_key='id',
                              column_defaults={'align': 'center', 'headerClasses': 'uppercase text-primary',
                                               'justify-content': 'center'}).classes('w-full')
        self.table.add_slot('body', ''' 
                            <q-tr :props="props">
                                <q-td v-for="col in props.cols" :key="col.name" :props="props" 
                                      :style="col.name === 'id' ? 'width: 15%;' : 'width: 10%;'" class="text-center">

                                    <template v-if="col.name === 'avatar'">
                                        <div class="flex justify-center">
                                            <img :src="props.row.avatar" class="w-32 h-32 rounded-full">
                                        </div>
                                    </template>

                                    <template v-else-if="col.name === 'id'">
                                        <div class="flex justify-center items-center gap-4 p-2">
                                            <q-btn color="red" dense icon="delete" size="md"
                                                @click="() => $parent.$emit('delete', props.row)">Usuń</q-btn>

                                            <q-btn v-if="!props.row.editing" color="primary" dense icon="edit" size="md"
                                                @click="props.row.editing = true">Edytuj</q-btn>

                                            <q-btn v-else color="green" dense icon="save" size="md"
                                                @click="() => { 
                                                    $parent.$emit('edit', props.row); 
                                                    props.row.editing = false;
                                                }">Zapisz</q-btn>
                                        </div>
                                    </template>

                                    <template v-else>
                                        <q-input v-if="props.row.editing" v-model="props.row[col.name]" dense outlined 
                                                 :label="col.label" class="w-full"/>
                                        <span v-else class="block text-center">{{ col.value }}</span>
                                    </template>

                                </q-td>
                            </q-tr>
                        ''')
        self.table.on('delete', self.delete_user)
        self.table.on('edit', self.edit_user)
        self.update_table()

    def update_table(self):
        users = self.user_service.load_data()
        self.table.rows.clear()
        for user in users:
            self.table.rows.append({
                'name': user["name"],
                'surname': user["surname"],
                'username': user["username"],
                'password': user["password"],
                'pesel': user["pesel"],
                'avatar': user["avatar"],
                'id': user['id']
            })
        self.table.update()

    def delete_user(self, e: events.GenericEventArguments):
        user_id = e.args.get('id')
        if self.user_service.delete_user(user_id):
            ui.notify("✅ Użytkownik usunięty!", color="green")
        else:
            ui.notify("❌ Błąd: Użytkownik nie został znaleziony!", color="red")
        self.update_table()

    def edit_user(self, e: events.GenericEventArguments):
        user_data = e.args.copy()
        user_id = user_data.pop('id')
        user_data.pop('editing')
        if self.user_service.edit_user(user_id, user_data):
            ui.notify("✅ Zmiany zapisane!", color="green")
        else:
            ui.notify("❌ Błąd: Użytkownik nie znaleziony!", color="red")
        self.update_table()