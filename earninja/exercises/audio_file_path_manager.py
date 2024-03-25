from pathlib import Path


class AudioFilePathManager:
    @classmethod
    def get_interval_audio_path(cls, interval_instance, filename=None):
        # keep filename arg unused to avoid circularity
        return Path('audio') / f"interval_{interval_instance.id}.mp3"
