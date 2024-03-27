from django.test import TestCase
from django.contrib.auth import get_user_model

from exercises.models import (
    Interval,
    IntervalInstance,
    IntervalsExercise,
    IntervalsExerciseSettings,
    IntervalAnswer,
    ExerciseScore,
)


class IntervalModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Interval.objects.create(name="b3", num_semitones=3)
        Interval.objects.create(name="5", num_semitones=7)

    def test_object_name_is_interval_name(self):
        interval_b3 = Interval.objects.get(id=1)
        interval_5 = Interval.objects.get(id=2)

        self.assertEqual(str(interval_b3), "b3")
        self.assertEqual(str(interval_5), "5")


class IntervalInstanceModelTests(TestCase):
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

        self.assertEqual(interval_instance_1.get_audio_url(), "/media/audio/interval_instance_1.mp3")
        self.assertEqual(interval_instance_2.get_audio_url(), "/media/audio/interval_instance_2.mp3")


class IntervalsExerciseModelTests(TestCase):
    def setUp(self):
        # create settings
        settings = IntervalsExerciseSettings.objects.create(
            lowest_octave=3, 
            highest_octave=5,
        )
        settings.allowed_intervals.set([
            Interval.objects.create(name="b3", num_semitones=3),
            Interval.objects.create(name="#4", num_semitones=6),
            Interval.objects.create(name="5", num_semitones=7)
        ])
        # create interval instances for question and answers
        question = IntervalInstance.objects.create(start_note=4*12, interval=settings.allowed_intervals.get(name="b3"))
        answers = [
            question,
            IntervalInstance.objects.create(start_note=4*12, interval=settings.allowed_intervals.get(name="#4")),
            IntervalInstance.objects.create(start_note=4*12, interval=settings.allowed_intervals.get(name="5")),
        ]
        # create a user
        User = get_user_model()
        test_user = User.objects.create_user(username='test_user', password='r6S6FrpHzFqf')
        test_user.save()
        # create score object
        score = ExerciseScore.objects.create()
        # finally, create intervals exercise object
        self.exercise = IntervalsExercise.objects.create(
            question=question,
            user=test_user,
            settings=settings,
            score=score,
        )
        self.exercise.answers.set(answers)
        # set correct answer
        answer = IntervalAnswer.objects.get(exercise=self.exercise, interval_instance=question)
        answer.is_correct = True
        answer.save()
    
    def test_object_name_is_exercise_for_user(self):
        self.assertEqual(str(self.exercise), 'exercise for user: test_user')
    
    def test_through_table_object_name_is_interval_name(self):
        answer_interval_instance = self.exercise.answers.get(interval__name="#4")
        answer = IntervalAnswer.objects.get(exercise=self.exercise, interval_instance=answer_interval_instance)
        self.assertEqual(str(answer), '#4')
    
    def test_deleting_answer_does_not_delete_exercise(self):
        self.assertEqual(self.exercise.answers.count(), 3)
        self.exercise.answers.get(interval__name="#4").delete()

        self.assertEqual(IntervalsExercise.objects.count(), 1)
        exercise = IntervalsExercise.objects.get(id=1)
        self.assertEqual(exercise.answers.count(), 2)
    
    def test_deleting_question_does_not_delete_exercise(self):
        self.exercise.answers.get(interval__name="b3").delete()

        self.assertEqual(IntervalsExercise.objects.count(), 1)
        exercise = IntervalsExercise.objects.get(id=1)
        self.assertIsNone(exercise.question)

    def test_deleting_user_deletes_exercise(self):
        self.exercise.user.delete()
        self.assertEqual(IntervalsExercise.objects.count(), 0)
    
    def test_deleting_score_does_not_delete_exercise(self):
        ExerciseScore.objects.get(id=1).delete()
        self.assertEqual(IntervalsExercise.objects.count(), 1)
        exercise = IntervalsExercise.objects.get(id=1)
        self.assertIsNone(exercise.score)
    
    def test_deleting_settings_does_not_delete_exercise(self):
        IntervalsExerciseSettings.objects.get(id=1).delete()
        self.assertEqual(IntervalsExercise.objects.count(), 1)
        exercise = IntervalsExercise.objects.get(id=1)
        self.assertIsNone(exercise.settings)
    

class IntervalsExerciseSettingsModelTests(TestCase):
    def setUp(self):
        self.settings = IntervalsExerciseSettings.objects.create(
            lowest_octave=3, 
            highest_octave=5,
        )
        self.settings.allowed_intervals.set([
            Interval.objects.create(name="b3", num_semitones=3),
            Interval.objects.create(name="#4", num_semitones=6),
            Interval.objects.create(name="5", num_semitones=7)
        ])

    def test_object_name_is_as_expected_with_no_exericse(self):
        self.assertEqual(
            str(self.settings),
            "settings (id=1), no exercise"
        )
    
    def test_object_name_is_as_expected_with_exericse(self):
        User = get_user_model()
        test_user = User.objects.create_user(username='test_user', password='r6S6FrpHzFqf')
        test_user.save()
        self.exercise = IntervalsExercise.objects.create(
            question=None,
            user=test_user,
            settings=self.settings,
        )
        self.assertEqual(
            str(self.settings),
            "settings for exercise for user: test_user"
        )


class ExerciseScoreModelTests(TestCase):
    def setUp(self):
        self.score = ExerciseScore.objects.create(
            num_correct_answers=3,
            num_all_answers=9,
        )
    
    def test_object_name_is_correct_slash_all_and_then_percentage(self):
        self.assertEqual(str(self.score), "3/9 (33.33%)")

    def test_display_as_percentage(self):
        self.assertEqual(self.score.display_as_percentage(), "33.33%")
