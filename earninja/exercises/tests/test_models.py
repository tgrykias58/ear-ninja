from django.test import TestCase

from exercises.models import (
    Interval,
    IntervalInstance,
)


class IntervalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Interval.objects.create(name="b3", num_semitones=3)
        Interval.objects.create(name="5", num_semitones=7)

    def test_object_name_is_interval_name(self):
        interval_b3 = Interval.objects.get(id=1)
        interval_5 = Interval.objects.get(id=2)

        self.assertEqual(str(interval_b3), "b3")
        self.assertEqual(str(interval_5), "5")


class IntervalInstanceTests(TestCase):
    def setUp(self):
        self.interval_b3 = Interval.objects.create(name="b3", num_semitones=3)

        IntervalInstance.objects.create(start_note=4*12, interval=self.interval_b3)
        IntervalInstance.objects.create(start_note=4*12 + 5, interval=self.interval_b3)
    
    def test_object_name_is_interval_name_comma_start_note(self):
        interval_instance_1 = IntervalInstance.objects.get(id=1)
        interval_instance_2 = IntervalInstance.objects.get(id=2)

        self.assertEqual(str(interval_instance_1), "b3, start note: 48")
        self.assertEqual(str(interval_instance_2), "b3, start note: 53")
    
    def test_get_audio_url(self):
        interval_instance_1 = IntervalInstance.objects.get(id=1)
        interval_instance_2 = IntervalInstance.objects.get(id=2)

        self.assertEqual(interval_instance_1.get_audio_url(), "/media/audio/interval_1.mp3")
        self.assertEqual(interval_instance_2.get_audio_url(), "/media/audio/interval_2.mp3")
