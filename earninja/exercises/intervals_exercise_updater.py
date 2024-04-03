from django.conf import settings

from exercises.models import (
    IntervalsExerciseSettings,
    Interval
)
from exercises.music_theory_utils import get_num_semitones
from exercises.tasks import update_interval_instance_audio


class IntervalsExerciseUpdater:
    def __init__(self, exercise):
        self.exercise = exercise

    def set_default_settings(self):
        IntervalsExerciseSettings.objects.filter(exercise=self.exercise).delete()

        default_settings = IntervalsExerciseSettings.objects.create(
            lowest_octave=settings.INTERVALS_DEFAULT_LOWEST_OCTAVE,
            highest_octave=settings.INTERVALS_DEFAULT_HIGHEST_OCTAVE
        )
        self._set_allowed_intervals(default_settings, settings.INTERVALS_DEFAULT_ALLOWED_INTERVALS)
        self.exercise.settings = default_settings
        self.exercise.save()
    
    def save_audio_files(self):
        # question interval should be among answers
        # so it's not necessary to update audio file for it separately
        for answer in self.exercise.answers.all():
            if not answer.audio:
                if settings.USE_CELERY:
                    update_interval_instance_audio.delay(answer.id)
                else:
                    update_interval_instance_audio(answer.id)
    
    def _set_allowed_intervals(self, exercise_settings, allowed_interval_names):
        allowed_intervals = [
            Interval.objects.get_or_create(
                num_semitones=get_num_semitones(interval_name),
                defaults={"name": interval_name}
            )[0]
            for interval_name in allowed_interval_names
        ]
        exercise_settings.allowed_intervals.set(allowed_intervals)
