import shutil
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files import File

from exercises.models import (
    IntervalsExercise, 
    IntervalsExerciseSettings,
    Interval,
    IntervalInstance,
    ExerciseScore,
)
from exercises.intervals_exercise_updater import IntervalsExerciseUpdater


@override_settings(MEDIA_ROOT=Path(settings.MEDIA_ROOT) / "test")
class IntervalsExerciseUpdaterTests(TestCase):
    def setUp(self):
        # use test media directory for tests
        self.test_media_dir = Path(settings.MEDIA_ROOT)
        self.test_media_dir.mkdir(parents=True, exist_ok=True)
        # create custom settings
        self.custom_settings = IntervalsExerciseSettings.objects.create(
            lowest_octave=2, 
            highest_octave=12,
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
    
    def tearDown(self):
        shutil.rmtree(self.test_media_dir)

    def test_set_default_settings_works_with_no_existing_previous_settings(self):
        self.assertEqual(IntervalsExerciseSettings.objects.count(), 1)
        self.updater.set_default_settings()
        # check exercise settings created
        self.assertEqual(IntervalsExerciseSettings.objects.count(), 2)
        # check if exercise settings are set to default
        exercise = IntervalsExercise.objects.get(id=self.updater.exercise.id)
        self._assertSettingsAreDefault(exercise)

    def test_set_default_settings_overrides_existing_settings(self):
        # set custom settings
        exercise = IntervalsExercise.objects.get(id=self.updater.exercise.id)
        exercise.settings = self.custom_settings
        exercise.save()
        self.assertEqual(IntervalsExerciseSettings.objects.count(), 1)
        self.updater.set_default_settings()
        # check if old exercise settings object was deleted
        self.assertEqual(IntervalsExerciseSettings.objects.count(), 1)
        # check if exercise settings are set to default
        exercise = IntervalsExercise.objects.get(id=self.updater.exercise.id)
        self._assertSettingsAreDefault(exercise)
    
    def _assertSettingsAreDefault(self, exercise):
        self.assertEqual(exercise.settings.lowest_octave, settings.INTERVALS_DEFAULT_LOWEST_OCTAVE)
        self.assertEqual(exercise.settings.highest_octave, settings.INTERVALS_DEFAULT_HIGHEST_OCTAVE)

        actual_allowed_interval_names = sorted([interval.name for interval in exercise.settings.allowed_intervals.all()])
        self.assertListEqual(actual_allowed_interval_names, sorted(settings.INTERVALS_DEFAULT_ALLOWED_INTERVALS))
    
    @override_settings(USE_CELERY=True)
    @patch('exercises.intervals_exercise_updater.update_interval_instance_audio')
    def test_save_audio_files_with_celery(self, mock_update_interval_instance_audio):
        exercise = self._prepare_exercise_object()       
        self.updater.save_audio_files()
        # update_interval_instance_audio.delay gets called because USE_CELERY=True
        # it's called only for intervals b3 and 5
        # bacause interval #4 already has a dummy file associated with audio field
        self.assertEqual(mock_update_interval_instance_audio.delay.call_count, 2)
        mock_update_interval_instance_audio.delay.assert_any_call(
             exercise.answers.get(interval__name="b3").id
        )
        mock_update_interval_instance_audio.delay.assert_any_call(
             exercise.answers.get(interval__name="5").id
        )
    
    @override_settings(USE_CELERY=False)
    @patch('exercises.intervals_exercise_updater.update_interval_instance_audio')
    def test_save_audio_files_without_celery(self, mock_update_interval_instance_audio):
        exercise = self._prepare_exercise_object()
        self.updater.save_audio_files()
        # update_interval_instance_audio gets called because USE_CELERY=False
        # it's called only for intervals b3 and 5
        # bacause interval #4 already has a dummy file associated with audio field
        self.assertEqual(mock_update_interval_instance_audio.call_count, 2)
        mock_update_interval_instance_audio.assert_any_call(
             exercise.answers.get(interval__name="b3").id
        )
        mock_update_interval_instance_audio.assert_any_call(
             exercise.answers.get(interval__name="5").id
        )

    def _prepare_exercise_object(self):
        exercise = IntervalsExercise.objects.get(id=self.updater.exercise.id)
        exercise.settings = self.custom_settings
        exercise.save()
        self._set_question_and_answers(exercise)
        # create a dummy file only for answer interval #4
        interval_instance_with_file = exercise.answers.get(interval__name="#4")
        self._set_dummy_audio_file(interval_instance_with_file)
        return exercise
    
    def _set_question_and_answers(self, exercise):
        # create interval instances for question and answers
        question = IntervalInstance.objects.create(start_note=4*12, interval=exercise.settings.allowed_intervals.get(name="b3"))
        answers = [
            question,
            IntervalInstance.objects.create(start_note=4*12, interval=exercise.settings.allowed_intervals.get(name="#4")),
            IntervalInstance.objects.create(start_note=4*12, interval=exercise.settings.allowed_intervals.get(name="5")),
        ]
        exercise.question = question
        exercise.save()
        exercise.answers.set(answers)

    def _set_dummy_audio_file(self, interval_instance):
        # create dummy file
        file_path = self.test_media_dir / "audio" / "interval_instance_audio.mp3"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(b"small file")
        # set this file to audio field
        with file_path.open(mode="rb") as f:
            interval_instance.audio = File(f, name=file_path.name)
            interval_instance.save()
        # clean up the original audio file
        # it doesn't delete the copy of the file set to the audio field
        file_path.unlink()
