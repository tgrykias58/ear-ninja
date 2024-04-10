from django.test import TestCase

from exercises.forms import IntervalsExerciseSettingsForm


class IntervalsExerciseSettingsFormTests(TestCase):
    def test_lowest_octave_larger_than_highest_octave_raises_error(self):
        form = IntervalsExerciseSettingsForm(
            data={
            'lowest_octave': 1,
            'highest_octave': -1,
            'allowed_intervals': ["b2", "b7", "6"]
        })
        self.assertIn("Lowest octave has to be less than or equal to highest octave", form.errors['__all__'])
    
    def test_lowest_octave_equal_highest_octave_passes_validation(self):
        form = IntervalsExerciseSettingsForm(
            data={
            'lowest_octave': 1,
            'highest_octave': 1,
            'allowed_intervals': ["b2", "b7", "6"]
        })
        self.assertIsNone(form.errors.get('__all__'))
