from django.test import TestCase

from exercises.file_path_manager import FilePathManager
from exercises.models import (
    Interval,
    IntervalInstance,
)


class FilePathManagerTests(TestCase):
    def setUp(self):
        self.interval_b3 = Interval.objects.create(name="b3", num_semitones=3)

        self.interval_instance_1 = IntervalInstance.objects.create(start_note=4*12, interval=self.interval_b3)
        self.interval_instance_2 = IntervalInstance.objects.create(start_note=4*12 + 5, interval=self.interval_b3)

    def test_get_interval_audio_path(self):
        self.assertEqual(
            str(FilePathManager.get_interval_audio_path(self.interval_instance_1)), 
            "audio/interval_1.mp3"
        )
        self.assertEqual(
            str(FilePathManager.get_interval_audio_path(self.interval_instance_2)), 
            "audio/interval_2.mp3"
        )
