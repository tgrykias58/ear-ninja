from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings

from exercises.models import (
    IntervalsExercise, 
    IntervalsExerciseSettings,
    Interval,
    ExerciseScore,
)
from exercises.intervals_exercise_updater import IntervalsExerciseUpdater


class IntervalsExerciseUpdaterTests(TestCase):
    def setUp(self):
        # create custom settings
        self.custom_settings = IntervalsExerciseSettings.objects.create(
            lowest_octave=2, 
            highest_octave=6,
        )
        self.custom_settings.allowed_intervals.set([
            Interval.objects.create(name="b3", num_semitones=3),
            Interval.objects.create(name="#4", num_semitones=6),
            Interval.objects.create(name="5", num_semitones=7)
        ])
        # create a user
        User = get_user_model()
        test_user = User.objects.create_user(username='test_user', password='r6S6FrpHzFqf')
        test_user.save()
        # create score object
        score = ExerciseScore.objects.create()
        # create intervals exercise object
        exercise = IntervalsExercise.objects.create(
            question=None,
            settings=None,
            user=test_user,
            score=score,
        )
        # create updater for this exercise
        self.updater = IntervalsExerciseUpdater(exercise)

    def test_set_default_settings_works_with_no_existing_previous_settings(self):
        self.assertEqual(IntervalsExerciseSettings.objects.count(), 1)
        self.updater.set_default_settings()
        # check exercise settings created
        self.assertEqual(IntervalsExerciseSettings.objects.count(), 2)
        
        exercise = IntervalsExercise.objects.get(id=self.updater.exercise.id)
        self._assertSettingsAreDefault(exercise)

    def test_set_default_settings_overrides_existing_settings(self):
        # set custom settings
        exercise = IntervalsExercise.objects.get(id=self.updater.exercise.id)
        exercise.settings = self.custom_settings
        exercise.save()

        self.assertEqual(IntervalsExerciseSettings.objects.count(), 1)
        self.updater.set_default_settings()
        # check if old settings deleted
        self.assertEqual(IntervalsExerciseSettings.objects.count(), 1)
        
        exercise = IntervalsExercise.objects.get(id=self.updater.exercise.id)
        self._assertSettingsAreDefault(exercise)
    
    def _assertSettingsAreDefault(self, exercise):
        self.assertEqual(exercise.settings.lowest_octave, settings.INTERVALS_DEFAULT_LOWEST_OCTAVE)
        self.assertEqual(exercise.settings.highest_octave, settings.INTERVALS_DEFAULT_HIGHEST_OCTAVE)

        actual_allowed_interval_names = sorted([interval.name for interval in exercise.settings.allowed_intervals.all()])
        self.assertListEqual(actual_allowed_interval_names, sorted(settings.INTERVALS_DEFAULT_ALLOWED_INTERVALS))
