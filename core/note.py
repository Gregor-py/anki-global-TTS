from core.config import config
from core.anki_connect import AnkiConnect

anki_connect = AnkiConnect(config.get_anki_connect_url())

class Note:
    def __init__(self, note_id):
        self.id = note_id
        self.note_info = anki_connect.invoke('notesInfo', notes=[note_id])[0]
        note_type = config.get_note_type_by_name(self.note_info['modelName'])
        if note_type is None:
            raise ValueError(f"Note type '{self.note_info['modelName']}' not found in config.")
        self.note_type = note_type

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

    def audio_field_is_empty(self):
        audio_field = self.get_field(self.note_type.audio_field)
        return audio_field == '' # need to check if the field contains audio not just an empty string

    def set_audio_field(self, value):
        self.change_field(self.note_type.audio_field, value)

    def get_text(self):
        self.get_field(self.note_info.text_field)