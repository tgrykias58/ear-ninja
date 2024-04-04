import random

from django.conf import settings

from exercises.models import (
    IntervalsExerciseSettings,
    ExerciseScore,
    Interval,
    IntervalInstance,
    IntervalAnswer,
)
from exercises.music_theory_utils import get_num_semitones
from exercises.tasks import update_interval_instance_audio


class IntervalsExerciseUpdater:
    NUM_NOTES_IN_OCTAVE = 12

    def __init__(self, exercise):
        self.exercise = exercise

    def generate_new_question(self):
        start_note = self._get_random_start_note()
        question_interval =  self._get_random_question_interval()
        self.exercise.question = IntervalInstance.objects.get_or_create(
            start_note=start_note,
            interval=question_interval
        )[0]
        self.exercise.save()
        answers = [
            IntervalInstance.objects.get_or_create(
                start_note=start_note,
                interval=interval
            )[0]
            for interval in self.exercise.settings.allowed_intervals.all()
        ]
        self.exercise.answers.set(answers, clear=True)
        self._set_correct_answer()

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
    
    def update_score(self, user_answer):
        score = ExerciseScore.objects.get_or_create(intervalsexercise=self.exercise)[0]
        correct_answer = self.exercise.answers.get(intervalanswer__is_correct=True)
        score.num_all_answers += 1
        if correct_answer == user_answer:
            score.num_correct_answers += 1
        score.save()
        self.exercise.save()
    
    def _get_random_start_note(self):
        lowest_note = self.exercise.settings.lowest_octave * self.NUM_NOTES_IN_OCTAVE
        highest_note = (self.exercise.settings.highest_octave + 1) * self.NUM_NOTES_IN_OCTAVE - 1
        return random.randint(lowest_note, highest_note)

    def _get_random_question_interval(self):
        return random.choice(self.exercise.settings.allowed_intervals.all())

    def _set_correct_answer(self):
        answer = IntervalAnswer.objects.get(exercise=self.exercise, interval_instance=self.exercise.question)
        answer.is_correct = True
        answer.save()

    def _set_allowed_intervals(self, exercise_settings, allowed_interval_names):
        allowed_intervals = [
            Interval.objects.get_or_create(
                num_semitones=get_num_semitones(interval_name),
                defaults={"name": interval_name}
            )[0]
            for interval_name in allowed_interval_names
        ]
        exercise_settings.allowed_intervals.set(allowed_intervals)
