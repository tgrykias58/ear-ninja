from django.test import SimpleTestCase

from exercises.music_theory_utils import get_num_semitones


class GetNumSemitonesTests(SimpleTestCase):
    def test_interval_name_without_sharp_or_flat(self):
        self.assertEqual(get_num_semitones("5"), 7)
    
    def test_interval_name_with_sharp(self):
        self.assertEqual(get_num_semitones("#4"), 6)

    def test_interval_name_with_flat(self):
        self.assertEqual(get_num_semitones("b7"), 10)

    def test_unison_is_zero_semitones(self):
        self.assertEqual(get_num_semitones("1"), 0)
