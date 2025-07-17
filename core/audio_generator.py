import elevenlabs
import uuid
import re
from core.config import config

class AudioGenerator:
    def __new__(cls, *args, **kwargs):
        raise TypeError(f"{cls.__name__} may not be instantiated.")


    @staticmethod
    def cleanhtml(raw_html):
        cleantext = re.sub(re.compile('<.*?>'), '', raw_html)
        return cleantext

    @staticmethod
    def prepare_text(text):
        no_html = AudioGenerator.cleanhtml(text)

        return no_html

    @staticmethod
    def generate_with_elevenlabs(text):
        elevenlabs.set_api_key(config.get_elevenlabs_api_key())
        try:
            text = AudioGenerator.prepare_text(text)
            audio = elevenlabs.generate(
                text=text,
                voice="Lily",
                model="eleven_multilingual_v2"
            )

            audio_id = uuid.uuid4()
            file_name = f'{audio_id}.mp3'
            path = config.get_media_path() + '\\' + file_name
            elevenlabs.save(audio, path)

            return file_name
        except:
            print('👺 problem with elevenlabs api')

