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

    def start(self):
        if not self._started:
            self._started = True
            print("App started.")
        else:
            print("App already started.")
