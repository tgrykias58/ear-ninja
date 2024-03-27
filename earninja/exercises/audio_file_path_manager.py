from pathlib import Path

from django.conf import settings


class AudioFilePathManager:
    @classmethod
    def get_interval_instance_audio_path(cls, interval_instance, filename=None):
        # keep filename arg unused to avoid circularity
        return Path('audio') / f"interval_instance_{interval_instance.id}.mp3"
    
    # base path for intermediate files (wav, midi, mp3) created by AudioSaver class
    @classmethod
    def get_intermediate_base_path(cls, audio_path):
        audio_path = Path(audio_path)
        return Path(settings.MEDIA_ROOT) / audio_path.parent / f'intermediate_{audio_path.stem}'
