import json

class Config:
    def __init__(self, config_file='config.json'):
        self.config_data = self._load_config(config_file)

    def _load_config(self, config_file):
        with open(config_file, 'r', encoding='utf-8') as configfile:
            return json.load(configfile)

    def get_days(self):
        return self.config_data.get('number_of_days_for_which_cards_were_created', 1)

    def get_media_path(self):
        return self.config_data.get('collection_media_path', '')

    def get_anki_connect_url(self):
        return self.config_data.get('anki_connect_url', '')

    def get_english_deck_name(self):
        return self.config_data.get('english_deck_name', '')

    def get_german_deck_name(self):
        return self.config_data.get('german_deck_name', '')
    
    def get_italian_deck_name(self):
        return self.config_data.get('italian_deck_name', '')

    def get_note_types(self):
        return self.config_data.get('note_types', [])

config = Config("config.json")