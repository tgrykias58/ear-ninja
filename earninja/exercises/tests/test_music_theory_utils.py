from django.test import SimpleTestCase

from exercises.music_theory_utils import (
    get_num_semitones,
    get_interval_long_name,
    get_interval_choices,
)


class MusicTheoryUtilsTests(SimpleTestCase):
    def test_get_num_semitones_interval_name_without_sharp_or_flat(self):
        self.assertEqual(get_num_semitones("5"), 7)
    
    def test_get_num_semitones_interval_name_with_sharp(self):
        self.assertEqual(get_num_semitones("#4"), 6)

    def test_get_num_semitones_interval_name_with_flat(self):
        self.assertEqual(get_num_semitones("b7"), 10)

    def test_get_num_semitones_unison_is_zero_semitones(self):
        self.assertEqual(get_num_semitones("1"), 0)

    def test_get_num_semitones_octave_is_twelve_semitones(self):
        self.assertEqual(get_num_semitones("8"), 12)
    
    def test_get_interval_long_name_without_sharp_or_flat(self):
        self.assertEqual(get_interval_long_name("5"), 'perfect fifth')
    
    def test_get_interval_long_name_with_sharp(self):
        self.assertEqual(get_interval_long_name("#6"), 'augmented sixth')
    
    def test_get_interval_long_name_with_flat(self):
        self.assertEqual(get_interval_long_name("b7"), 'minor seventh')

    def test_get_interval_long_name_for_unison(self):
        self.assertEqual(get_interval_long_name("1"), 'unison')
    
    def test_get_interval_long_name_for_octave(self):
        self.assertEqual(get_interval_long_name("8"), 'octave')

    def test_get_interval_choces(self):
        self.assertListEqual(
            get_interval_choices(),
            [('1', 'unison (1)'),
            ('b2', 'minor second (b2)'),
            ('2', 'major second (2)'),
            ('b3', 'minor third (b3)'),
            ('3', 'major third (3)'),
            ('4', 'perfect fourth (4)'),
            ('#4', 'augmented fourth (#4)'),
            ('5', 'perfect fifth (5)'),
            ('b6', 'minor sixth (b6)'),
            ('6', 'major sixth (6)'),
            ('b7', 'minor seventh (b7)'),
            ('7', 'major seventh (7)')]
        )
