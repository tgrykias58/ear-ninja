from django.db import models

from exercises.audio_file_path_manager import AudioFilePathManager


class Interval(models.Model):
    num_semitones = models.IntegerField()
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class IntervalInstance(models.Model):
    audio = models.FileField(upload_to=AudioFilePathManager.get_interval_audio_path)
    start_note = models.IntegerField()
    interval = models.ForeignKey(Interval, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.interval.name}, start note: {self.start_note}'
    
    # thanks to this method
    # the url can be accessed even before audio FileField is set
    def get_audio_url(self):
        audio_path = AudioFilePathManager.get_interval_audio_path(self)
        # https://docs.djangoproject.com/en/4.2/ref/models/fields/#django.db.models.FileField.storage
        # https://docs.djangoproject.com/en/4.2/ref/files/storage/#django.core.files.storage.Storage.url
        return self.audio.field.storage.url(audio_path)
