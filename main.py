from core.config import config
from core.global_tts import GlobalTTS
from core.note import Note
from core.audio_generator import AudioGenerator

app = GlobalTTS(config)

note = Note(1714124237261)

print(note.get_field("Word"))
audio = AudioGenerator.generate_with_elevenlabs("Hello, this is a test of the Eleven Labs audio generation system.")
print(audio)