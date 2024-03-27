from django.test import TestCase

from exercises.audio_file_path_manager import AudioFilePathManager
from exercises.models import (
    Interval,
    IntervalInstance,
)


class AudioFilePathManagerTests(TestCase):
    def setUp(self):
        self.interval_b3 = Interval.objects.create(name="b3", num_semitones=3)

        self.interval_instance_1 = IntervalInstance.objects.create(start_note=4*12, interval=self.interval_b3)
        self.interval_instance_2 = IntervalInstance.objects.create(start_note=4*12 + 5, interval=self.interval_b3)

    def test_get_interval_audio_path(self):
        self.assertEqual(
            str(AudioFilePathManager.get_interval_instance_audio_path(self.interval_instance_1)), 
            "audio/interval_instance_1.mp3"
        )
        self.assertEqual(
            str(AudioFilePathManager.get_interval_instance_audio_path(self.interval_instance_2)), 
            "audio/interval_instance_2.mp3"
        )
