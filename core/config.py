class Config:
    def __init__(self, config_file = 'config.txt'):
        self.config_data = self._load_config(config_file)

    def _load_config(self, config_file):
        config = {}
        with open(config_file, 'r', encoding='utf-8') as configfile:
            for line in configfile:
                line = line.strip()
                if ':' in line and not line.startswith('#') and not line.startswith('//'):
                    key, value = line.split(':', 1)
                    config[key] = value
        return config

    def get_days(self):
        return int(self.config_data.get('number_of_days_for_which_cards_were_created', 1))

    def get_media_path(self):
        return self.config_data.get('collection_media_path', '')
    
    def get_english_deck_name(self):
        return self.config_data.get('english_deck_name', '')

    def get_german_deck_name(self):
        return self.config_data.get('german_deck_name', '')
    
    def get_italian_deck_name(self):
        return self.config_data.get('italian_deck_name', '')

    def get_note_types(self): ## GEHT NUR WENN "Basic|Word|Audio" in der GLEICHEN ZEILE IST WIE note_types: 
        note_types_string = self.config_data.get('note_types', '')
        if note_types_string:
            return note_types_string.split('|')
        return []

    #def get_note_types(self): //maybe??
        # note_types_string = self.config_data.get('note_types', '')
        # if note_types_string:
        #     note_types = []
        #     for note_type in note_types_string.split('|'):
        #         parts = note_type.split(':')
        #         if len(parts) == 3:
        #             note_types.append({
        #                 "name": parts[0].strip(),
        #                 "text_field": parts[1].strip(), 
        #                 "audio_field": parts[2].strip()
        #             })
        #     return note_types
        # return []

        ##ALLES MIT DEBUGGER PRINT DURCHPROBIERT MÜSSTE FUNKTIONIEREN

config = Config("config.txt")