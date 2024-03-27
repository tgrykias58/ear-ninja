from pathlib import Path

from celery import shared_task
from django.core.files import File
from django.conf import settings

from exercises.models import IntervalInstance
from exercises.audio_saver import AudioSaver
from exercises.audio_file_path_manager import AudioFilePathManager


@shared_task()
def update_interval_instance_audio(interval_instance_id):
    # retrieve the interval instance object from the database
    interval_instance = IntervalInstance.objects.get(id=interval_instance_id)
    
    # manage paths
    relative_audio_path = AudioFilePathManager.get_interval_instance_audio_path(interval_instance)
    absolute_audio_path = Path(settings.MEDIA_ROOT) / relative_audio_path
    intermediate_audio_path = AudioFilePathManager.get_intermediate_base_path(relative_audio_path)

    # generate intermediate files: midi, wav, mp3
    audio_saver = AudioSaver(intermediate_audio_path)
    audio_saver.save_interval_instance_audio(
        interval_instance.start_note,
        interval_instance.interval.name
    )

    # delete the old audio file, if it already exists
    # thanks to django-cleanup app,
    # the mp3 file should be deleted here, together with audio field value
    interval_instance.audio.delete()
    # just in case there was a file with the same name but not associated with the audio field
    absolute_audio_path.unlink(missing_ok=True)

    # the exists() check helps to prevent creating multiple audio files
    # for the same interval instance due to race condtitons 
    # (i.e. due to many tasks for the same interval instance runnning at the same time)
    if not absolute_audio_path.exists():
        # associate the "intermediate" mp3 file with the audio field
        # it copies this file
        with intermediate_audio_path.with_suffix(".mp3").open(mode="rb") as f:
            interval_instance.audio = File(f, name=intermediate_audio_path.with_suffix(".mp3").name)
            interval_instance.save()

    # cleanup
    # delete the intermediate files
    # it does not delete the file associated with interval_instance.audio
    audio_saver.delete_files()
