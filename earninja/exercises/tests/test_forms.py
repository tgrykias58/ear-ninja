from django.test import TestCase

from exercises.forms import IntervalsExerciseSettingsForm
from exercises.models import IntervalsExerciseSettings, Interval


class IntervalsExerciseSettingsFormTests(TestCase):
    def setUp(self):
        self.exercise_settings = IntervalsExerciseSettings.objects.create(
            lowest_octave=3, 
            highest_octave=5,
        )
        self.exercise_settings.allowed_intervals.set([
            Interval.objects.create(name="b3", num_semitones=3, interval_type=1),
            Interval.objects.create(name="#4", num_semitones=6, interval_type=1),
            Interval.objects.create(name="5", num_semitones=7, interval_type=1)
        ])

    def test_lowest_octave_larger_than_highest_octave_raises_error(self):
        form = IntervalsExerciseSettingsForm(
            instance=self.exercise_settings,
            data={
            'lowest_octave': 1,
            'highest_octave': -1,
            'allowed_intervals': ["b2", "b7", "6"],
            'interval_type': 0
        })
        self.assertIn("Lowest octave has to be less than or equal to highest octave", form.errors['__all__'])
    
    def test_lowest_octave_equal_highest_octave_passes_validation(self):
        form = IntervalsExerciseSettingsForm(
            instance=self.exercise_settings,
            data={
            'lowest_octave': 1,
            'highest_octave': 1,
            'allowed_intervals': ["b2", "b7", "6"],
            'interval_type': 1
        })
        self.assertIsNone(form.errors.get('__all__'))
    
    def test_initial_values(self):
        form = IntervalsExerciseSettingsForm(instance=self.exercise_settings)
        self.assertListEqual(form.fields['allowed_intervals'].initial,  ['b3', '#4', '5'])
        self.assertEqual(form.fields['interval_type'].initial, 1)
