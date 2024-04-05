from django.test import SimpleTestCase, TestCase
from django.urls import reverse  

from django.contrib.auth import get_user_model


class ChooseExerciseViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        test_user = User.objects.create_user(username='just_user', password='r6S6FrpHzFqf')
        test_user.save()

    def test_url_exists_at_correct_location(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_url_available_by_name(self):  
        response = self.client.get(reverse("exercises:choose_exercise"))
        self.assertEqual(response.status_code, 200)

    def test_template_name_correct(self):  
        response = self.client.get(reverse("exercises:choose_exercise"))
        self.assertTemplateUsed(response, "exercises/choose_exercise.html")

    def test_template_content(self):
        response = self.client.get(reverse("exercises:choose_exercise"))
        self.assertContains(response, reverse("exercises:intervals_question"))
        self.assertContains(response, reverse("exercises:scale_degrees_question"))
    
    def test_logged_in_user_can_log_out(self):
        # test user logs in
        login = self.client.login(username='just_user', password='r6S6FrpHzFqf')
        # make sure login was successful
        self.assertTrue(login)

        response = self.client.get(reverse("exercises:choose_exercise"))
        # we show only the logout option to the user
        self.assertContains(response, reverse("logout"))
        # it doesn't make sense to show login option when user has already logged in
        self.assertNotContains(response, reverse("signup"))
        self.assertNotContains(response, reverse("login"))
    
    def test_logged_out_user_can_log_in(self):
        response = self.client.get(reverse("exercises:choose_exercise"))
        # user isn't logged in, so it doesn't make sense to show the logout option
        self.assertNotContains(response, reverse("logout"))
        # user can log in or sign up
        self.assertContains(response, reverse("signup"))
        self.assertContains(response, reverse("login"))


class IntervalsQuestionViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        test_user = User.objects.create_user(username='test_user', password='r6S6FrpHzFqf')
        test_user.save()
        self.client.login(username='test_user', password='r6S6FrpHzFqf')

    def test_url_exists_at_correct_location(self):
        response = self.client.get("/intervals/question")
        self.assertEqual(response.status_code, 200)

    def test_url_available_by_name(self):
        response = self.client.get(reverse("exercises:intervals_question"))
        self.assertEqual(response.status_code, 200)
    
    def test_redirect_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse("exercises:intervals_question"))
        self.assertRedirects(response, '/accounts/login/?next=/intervals/question')

    def test_template_name_correct(self):
        response = self.client.get(reverse("exercises:intervals_question"))
        self.assertTemplateUsed(response, "exercises/intervals_question.html")

    def test_template_content(self):
        response = self.client.get(reverse("exercises:intervals_question"))
        self.assertContains(response, "Repeat")


class ScaleDegreesQuestionViewTests(SimpleTestCase):
    def test_url_exists_at_correct_location(self):
        response = self.client.get("/scale-degrees/question")
        self.assertEqual(response.status_code, 200)

    def test_url_available_by_name(self):  
        response = self.client.get(reverse("exercises:scale_degrees_question"))
        self.assertEqual(response.status_code, 200)

    def test_template_name_correct(self):  
        response = self.client.get(reverse("exercises:scale_degrees_question"))
        self.assertTemplateUsed(response, "exercises/coming_soon.html")

    def test_template_content(self):
        response = self.client.get(reverse("exercises:scale_degrees_question"))
        self.assertContains(response, "coming soon")
        self.assertContains(response, "Scale Degrees")
        