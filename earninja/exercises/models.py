from django.db import models
from django.conf import settings

from exercises.audio_file_path_manager import AudioFilePathManager


class Interval(models.Model):
    num_semitones = models.IntegerField()
    name = models.CharField(max_length=30)

    class Meta:
        ordering = ['num_semitones']

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


class IntervalsExercise(models.Model):
    question = models.ForeignKey(IntervalInstance, null=True, on_delete=models.SET_NULL, related_name="exercises_with_interval_instance_as_question")
    answers = models.ManyToManyField(IntervalInstance, through="IntervalAnswer", related_name="exercises_with_interval_instance_as_answer")

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    settings = models.OneToOneField("IntervalsExerciseSettings", null=True, on_delete=models.SET_NULL, related_name="exercise")

    def __str__(self):
        return f'exercise for user: {self.user}'


class IntervalAnswer(models.Model):
    interval_instance = models.ForeignKey(IntervalInstance, on_delete=models.CASCADE)
    exercise = models.ForeignKey(IntervalsExercise, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.interval_instance.interval.name


class IntervalsExerciseSettings(models.Model):
    lowest_octave = models.IntegerField()
    highest_octave = models.IntegerField()
    allowed_intervals = models.ManyToManyField(Interval)

    def __str__(self):
        if hasattr(self, "exercise"):
            return f'settings for {self.exercise}'
        else:
            return f'settings (id={self.id}), no exercise'
