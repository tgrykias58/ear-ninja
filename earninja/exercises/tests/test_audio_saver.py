import shutil
from pathlib import Path

from django.test import SimpleTestCase
from django.conf import settings

from exercises.audio_saver import AudioSaver


class AudioSaverTests(SimpleTestCase):
    def setUp(self):
        self.test_media_dir = Path(settings.MEDIA_ROOT) / "test"
        self.test_media_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_media_dir)

    def test_save_interval_instance_audio(self):
        audio_path = self.test_media_dir / "interval_42"
        audio_saver = AudioSaver(audio_path)
        audio_saver.save_interval_instance_audio(start_note=4*12, interval_name="#4")

        saved_file_path = self.test_media_dir / "interval_42.mid"
        self.assertTrue(saved_file_path.is_file())
        self.assertGreaterEqual(saved_file_path.stat().st_size, 5)

        saved_file_path = self.test_media_dir / "interval_42.wav"
        self.assertTrue(saved_file_path.is_file())
        self.assertGreaterEqual(saved_file_path.stat().st_size, 500)

        saved_file_path = self.test_media_dir / "interval_42.mp3"
        self.assertTrue(saved_file_path.is_file())
        self.assertGreaterEqual(saved_file_path.stat().st_size, 500)

    def test_delete_files(self):
        file_path = self.test_media_dir / "interval_42.mid"
        file_path.write_bytes(b"content")
        self.assertTrue(file_path.is_file())

        file_path = self.test_media_dir / "interval_42.wav"
        file_path.write_bytes(b"content")
        self.assertTrue(file_path.is_file())
        
        file_path = self.test_media_dir / "interval_42.mp3"
        file_path.write_bytes(b"content")
        self.assertTrue(file_path.is_file())
        
        audio_path = self.test_media_dir / "interval_42"
        audio_saver = AudioSaver(audio_path)
        audio_saver.delete_files()

        file_path = self.test_media_dir / "interval_42.mid"
        self.assertFalse(file_path.exists())

        file_path = self.test_media_dir / "interval_42.wav"
        self.assertFalse(file_path.exists())

        file_path = self.test_media_dir / "interval_42.mp3"
        self.assertFalse(file_path.exists())

        # to make sure that there are no errors if files are already deleted
        audio_saver.delete_files()
