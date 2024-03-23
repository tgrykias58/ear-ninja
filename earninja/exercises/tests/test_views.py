from django.test import SimpleTestCase
from django.urls import reverse  


class ChooseExerciseViewTests(SimpleTestCase):
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


class IntervalsQuestionViewTests(SimpleTestCase):
    def test_url_exists_at_correct_location(self):
        response = self.client.get("/intervals/question")
        self.assertEqual(response.status_code, 200)

    def test_url_available_by_name(self):  
        response = self.client.get(reverse("exercises:intervals_question"))
        self.assertEqual(response.status_code, 200)

    def test_template_name_correct(self):  
        response = self.client.get(reverse("exercises:intervals_question"))
        self.assertTemplateUsed(response, "exercises/coming_soon.html")

    def test_template_content(self):
        response = self.client.get(reverse("exercises:intervals_question"))
        self.assertContains(response, "coming soon")
        self.assertContains(response, "Intervals")


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
        