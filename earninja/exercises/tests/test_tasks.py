from pathlib import Path
import shutil

from django.test import TransactionTestCase, override_settings
from django.conf import settings
from django.core.files import File

from exercises.models import Interval, IntervalInstance
from exercises.tasks import update_interval_instance_audio


@override_settings(MEDIA_ROOT=Path(settings.MEDIA_ROOT) / "test")
class UpdateIntervalInstanceAudioTaskTests(TransactionTestCase):
    def setUp(self):
        self.test_media_dir = Path(settings.MEDIA_ROOT)
        self.test_media_dir.mkdir(parents=True, exist_ok=True)

        interval_b3 = Interval.objects.create(name="b3", num_semitones=3)
        self.interval_instance = IntervalInstance.objects.create(start_note=4*12, interval=interval_b3)

    def tearDown(self):
        shutil.rmtree(self.test_media_dir)

    def test_mp3_file_saved(self):
        saved_file_path = self.test_media_dir / "audio" / f"interval_instance_{self.interval_instance.id}.mp3"
        self.assertFalse(saved_file_path.is_file())

        update_interval_instance_audio(self.interval_instance.id)

        self.assertTrue(saved_file_path.is_file())
        self.assertGreaterEqual(saved_file_path.stat().st_size, 500)

    def test_mp3_file_associated_with_interval_instance_audio_field(self):
        update_interval_instance_audio(self.interval_instance.id)

        interval_instance = IntervalInstance.objects.get(id=self.interval_instance.id)
        self.assertGreaterEqual(interval_instance.audio.file.size, 500)
        self.assertEqual(interval_instance.audio.name, f"audio/interval_instance_{self.interval_instance.id}.mp3")

    def test_intermediate_files_cleaned_up(self):
        update_interval_instance_audio(self.interval_instance.id)

        file_path = self.test_media_dir / "audio" / f"intermediate_interval_instance_{self.interval_instance.id}.mid"
        self.assertFalse(file_path.exists())

        file_path = self.test_media_dir / "audio" / f"intermediate_interval_instance_{self.interval_instance.id}.wav"
        self.assertFalse(file_path.exists())

        file_path = self.test_media_dir / "audio" / f"intermediate_interval_instance_{self.interval_instance.id}.mp3"
        self.assertFalse(file_path.exists())

    def test_mp3_file_replaced_if_already_exists_and_associated_with_audio_field(self):
        intermediate_file_path = self.test_media_dir / "audio" / f"intermediate_interval_instance_{self.interval_instance.id}.mp3"
        file_path = self.test_media_dir / "audio" / f"interval_instance_{self.interval_instance.id}.mp3"

        # create a dummy file
        intermediate_file_path.parent.mkdir(parents=True, exist_ok=True)
        intermediate_file_path.write_bytes(b"small file")

        # associate dummy file with audio field
        with intermediate_file_path.open(mode="rb") as f:
            self.interval_instance.audio = File(f, name=intermediate_file_path.name)
            self.interval_instance.save()
        intermediate_file_path.unlink()

        self.assertEqual(len(list(file_path.parent.glob("*.mp3"))), 1)
        self.assertEqual(file_path.stat().st_size, 10)

        update_interval_instance_audio(self.interval_instance.id)

        self.assertEqual(len(list(file_path.parent.glob("*.mp3"))), 1)
        self.assertGreaterEqual(file_path.stat().st_size, 500)
    
    def test_mp3_file_replaced_if_already_exists_and_not_associated_with_audio_field(self):
        file_path = self.test_media_dir / "audio" / f"interval_instance_{self.interval_instance.id}.mp3"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(b"small file")

        self.assertEqual(len(list(file_path.parent.glob("*.mp3"))), 1)
        self.assertEqual(file_path.stat().st_size, 10)

        update_interval_instance_audio(self.interval_instance.id)

        self.assertEqual(len(list(file_path.parent.glob("*.mp3"))), 1)
        self.assertGreaterEqual(file_path.stat().st_size, 500)
