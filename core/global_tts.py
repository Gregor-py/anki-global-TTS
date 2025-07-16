from core.anki_connect import AnkiConnect


class GlobalTTS:
    _instance = None

    def __new__(cls, config):
        if cls._instance is None:
            cls._instance = super(GlobalTTS, cls).__new__(cls)
        return cls._instance

    def __init__(self, config):
        if not hasattr(self, '_started'):
            self._started = False
            self.config = config
            self.anki_connect = AnkiConnect(config.get_anki_connect_url())

    def start(self):
        if not self._started:
            self._started = True
            print("App started.")
        else:
            print("App already started.")
