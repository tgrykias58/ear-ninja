from django.db import models
from django.db.models import UniqueConstraint 
from django.conf import settings

from exercises.audio_file_path_manager import AudioFilePathManager
from exercises.music_theory_utils import (
    get_interval_long_name,
    get_note_name,
    get_interval_type_choices,
    INTERVAL_TYPES,
)


class Interval(models.Model):
    num_semitones = models.IntegerField()
    name = models.CharField(max_length=30)
    interval_type = models.IntegerField(choices=get_interval_type_choices(), default=0)

    class Meta:
        ordering = ['num_semitones']
        constraints = [
            UniqueConstraint(  
                fields=['num_semitones', 'interval_type'],
                name='interval_is_defined_by_num_semitones_and_type'
            )
        ]

    def __str__(self):
        return f'{get_interval_long_name(self.name)}, {INTERVAL_TYPES[self.interval_type]}'


class IntervalInstance(models.Model):
    audio = models.FileField(upload_to=AudioFilePathManager.get_interval_instance_audio_path)
    start_note = models.IntegerField()
    interval = models.ForeignKey(Interval, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            UniqueConstraint(  
                fields=['start_note', 'interval'],
                name='interval_instance_is_defined_by_interval_and_start_note'
            )
        ]
        
    def __str__(self):
        return f'{self.interval}, start note: {get_note_name(self.start_note)}'
    
    # thanks to this method
    # the url can be accessed even before audio FileField is set
    def get_audio_url(self):
        audio_path = AudioFilePathManager.get_interval_instance_audio_path(self)
        # https://docs.djangoproject.com/en/4.2/ref/models/fields/#django.db.models.FileField.storage
        # https://docs.djangoproject.com/en/4.2/ref/files/storage/#django.core.files.storage.Storage.url
        return self.audio.field.storage.url(audio_path)


class IntervalsExercise(models.Model):
    question = models.ForeignKey(IntervalInstance, null=True, on_delete=models.SET_NULL, related_name="exercises_with_interval_instance_as_question")
    answers = models.ManyToManyField(IntervalInstance, through="IntervalAnswer", related_name="exercises_with_interval_instance_as_answer")

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    settings = models.OneToOneField("IntervalsExerciseSettings", null=True, on_delete=models.SET_NULL, related_name="exercise")
    score = models.OneToOneField("ExerciseScore", null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'intervals exercise for user: {self.user}'


class IntervalAnswer(models.Model):
    interval_instance = models.ForeignKey(IntervalInstance, on_delete=models.CASCADE)
    exercise = models.ForeignKey(IntervalsExercise, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"answer: {self.interval_instance.interval} for user: {self.exercise.user}"


class IntervalsExerciseSettings(models.Model):
    lowest_octave = models.IntegerField()
    highest_octave = models.IntegerField()
    allowed_intervals = models.ManyToManyField(Interval)

    def __str__(self):
        if hasattr(self, "exercise"):
            return f'settings for {self.exercise}'
        else:
            return f'settings (id={self.id}), no exercise'


class ExerciseScore(models.Model):
    num_correct_answers = models.IntegerField(default=0)
    num_all_answers = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.num_correct_answers}/{self.num_all_answers} ({self.display_as_percentage()})'

    def display_as_percentage(self):
        return f'{100 * self.num_correct_answers / self.num_all_answers:.2f}%' if self.num_all_answers else "100.00%"
