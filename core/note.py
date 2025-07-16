from core.config import config
from core.anki_connect import AnkiConnect

anki_connect = AnkiConnect(config.get_anki_connect_url())

class Note:
    def __init__(self, note_id):
        self.id = note_id
        self.note_info = anki_connect.invoke('notesInfo', notes=[note_id])[0]
        note_types = config.get_note_types()
        print(note_types)

    def get_field(self, field_name):
        if field_name in self.note_info['fields']:
            return self.note_info['fields'][field_name]['value']
        else:
            raise ValueError(f"Field '{field_name}' does not exist in note {self.id}.")


    def change_field(self, field_name, new_value):
        if field_name in self.note_info['fields']:
            self.note_info['fields'][field_name]['value'] = new_value
            anki_connect.invoke('updateNoteFields', note=self.note_info)
        else:
            raise ValueError(f"Field '{field_name}' does not exist in note {self.id}.")

