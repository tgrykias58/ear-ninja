import shutil
from pathlib import Path
from unittest.mock import patch

from mingus.containers import Note

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


@override_settings(
    MEDIA_ROOT=Path(settings.MEDIA_ROOT) / "test",
    INTERVALS_EXERCISE_DEFAULT_LOWEST_OCTAVE=3,
    INTERVALS_EXERCISE_DEFAULT_HIGHEST_OCTAVE=5,
    INTERVALS_EXERCISE_DEFAULT_ALLOWED_INTERVALS=["1", "b3", "3", "4", "5"],
    INTERVALS_EXERCISE_DEFAULT_INTERVAL_TYPE=0,
)
class IntervalsExerciseUpdaterTests(TestCase):
    def setUp(self):
        # use test media directory for tests
        self.test_media_dir = Path(settings.MEDIA_ROOT)
        self.test_media_dir.mkdir(parents=True, exist_ok=True)
        # create custom settings
        self.custom_settings = IntervalsExerciseSettings.objects.create(
            lowest_octave=-1, 
            highest_octave=1,
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
        # create intervals exercise object
        exercise = IntervalsExercise.objects.create(
            question=None,
            settings=None,
            user=test_user,
            score=None,
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
        self.assertEqual(exercise.settings.lowest_octave, settings.INTERVALS_EXERCISE_DEFAULT_LOWEST_OCTAVE)
        self.assertEqual(exercise.settings.highest_octave, settings.INTERVALS_EXERCISE_DEFAULT_HIGHEST_OCTAVE)
        actual_allowed_interval_names = sorted([interval.name for interval in exercise.settings.allowed_intervals.all()])
        self.assertListEqual(actual_allowed_interval_names, sorted(settings.INTERVALS_EXERCISE_DEFAULT_ALLOWED_INTERVALS))
        for interval in exercise.settings.allowed_intervals.all():
            self.assertEqual(interval.interval_type, settings.INTERVALS_EXERCISE_DEFAULT_INTERVAL_TYPE)
    
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
        question = IntervalInstance.objects.create(start_note=5, interval=exercise.settings.allowed_intervals.get(name="b3"))
        answers = [
            question,
            IntervalInstance.objects.create(start_note=5, interval=exercise.settings.allowed_intervals.get(name="#4")),
            IntervalInstance.objects.create(start_note=5, interval=exercise.settings.allowed_intervals.get(name="5")),
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
    
    def test_generate_new_question(self):
        self.updater.exercise.settings = self.custom_settings
        self.updater.exercise.save()

        self.updater.generate_new_question()

        exercise = IntervalsExercise.objects.get(id=self.updater.exercise.id)
        allowed_intervals_names = [interval.name for interval in self.custom_settings.allowed_intervals.all()]
        
        self.assertIn(exercise.question.interval.name, allowed_intervals_names)
        self.assertListEqual(sorted([answer.interval.name for answer in exercise.answers.all()]), sorted(allowed_intervals_names))
        for answer in exercise.answers.all():
            self.assertEqual(exercise.question.start_note, answer.start_note)
        self.assertGreaterEqual(Note().from_int(exercise.question.start_note).octave, self.custom_settings.lowest_octave)
        self.assertLessEqual(Note().from_int(exercise.question.start_note).octave, self.custom_settings.highest_octave)
        self.assertEqual(exercise.answers.get(intervalanswer__is_correct=True), exercise.question)
    
    @patch.object(IntervalsExerciseUpdater, '_get_random_question_interval')
    @patch.object(IntervalsExerciseUpdater, '_get_random_start_note', side_effect=[3, 3])
    def test_generate_new_question_clears_previous_correct_answer(
        self,
        mock__get_random_start_note, 
        mock_get_random_question_interval
    ):
        mock_get_random_question_interval.side_effect = [
            self.custom_settings.allowed_intervals.get(name="b3"),
            self.custom_settings.allowed_intervals.get(name="#4"),
        ]
        self.updater.exercise.settings = self.custom_settings
        self.updater.exercise.save()

        self.updater.generate_new_question()
        exercise = IntervalsExercise.objects.get(id=self.updater.exercise.id)
        self.assertEqual(
            exercise.answers.get(intervalanswer__is_correct=True), 
            IntervalInstance.objects.get(interval__name="b3", start_note=3), 
        )

        self.updater.generate_new_question()
        exercise = IntervalsExercise.objects.get(id=self.updater.exercise.id)
        correct_answers = exercise.answers.filter(intervalanswer__is_correct=True)
        # check that previous correct answer is no longer marked as correct
        self.assertNotIn(IntervalInstance.objects.get(interval__name="b3", start_note=3), correct_answers)
        self.assertEqual(correct_answers.count(), 1)
        self.assertEqual(
            correct_answers.first(), 
            IntervalInstance.objects.get(interval__name="#4", start_note=3), 
        )

    def test_update_score_correct_answer(self):
        self.updater.exercise.settings = self.custom_settings
        self.updater.exercise.save()
        self.updater.generate_new_question()

        exercise = IntervalsExercise.objects.get(id=self.updater.exercise.id)
        self.updater.update_score(exercise.question)
        exercise = IntervalsExercise.objects.get(id=self.updater.exercise.id)
        self.assertEqual(exercise.score.num_all_answers, 1)
        self.assertEqual(exercise.score.num_correct_answers, 1)

    def test_update_score_wrong_answer(self):
        self.updater.exercise.settings = self.custom_settings
        self.updater.exercise.save()
        self.updater.generate_new_question()

        exercise = IntervalsExercise.objects.get(id=self.updater.exercise.id)
        wrong_answer = exercise.answers.exclude(id=exercise.question.id).first()
        self.updater.update_score(wrong_answer)
        exercise = IntervalsExercise.objects.get(id=self.updater.exercise.id)
        self.assertEqual(exercise.score.num_all_answers, 1)
        self.assertEqual(exercise.score.num_correct_answers, 0)
    
    def test_reset_score(self):
        self.updater.reset_score()
        score = ExerciseScore.objects.get(intervalsexercise=self.updater.exercise)
        self.assertEqual(score.num_correct_answers, 0)
        self.assertEqual(score.num_all_answers, 0)
        score.num_correct_answers = 10
        score.num_all_answers = 24
        score.save()
        self.updater.reset_score()
        score = ExerciseScore.objects.get(intervalsexercise=self.updater.exercise)
        self.assertEqual(score.num_correct_answers, 0)
        self.assertEqual(score.num_all_answers, 0)
    
    def test_set_allowed_intervals(self):
        Interval.objects.create(name="b3", num_semitones=3, interval_type=1)
        Interval.objects.create(name="#4", num_semitones=6, interval_type=1)
        Interval.objects.create(name="5", num_semitones=7, interval_type=1)
        self.updater.set_default_settings()
        self.updater.set_allowed_intervals(["b2", "b5", "#2", '5'], interval_type=1)
        exercise = IntervalsExercise.objects.get(id=self.updater.exercise.id)
        actual_allowed_interval_names = sorted([interval.name for interval in exercise.settings.allowed_intervals.all()])
        # some names of intervals are different
        # because interval objects with the same numbers of semitones but alternative names
        # have been already created
        self.assertListEqual(actual_allowed_interval_names, sorted(['b2', 'b3', '#4', '5']))
        for interval in exercise.settings.allowed_intervals.all():
            self.assertEqual(interval.interval_type, 1)
