from core.config import config
from core.global_tts import GlobalTTS
from core.note import Note

app = GlobalTTS(config)

note = Note(1714124237261)

print(note.get_field("Word"))