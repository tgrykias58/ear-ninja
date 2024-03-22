from django.test import TestCase
from django.urls import reverse

class ChooseExerciseViewTests(TestCase):
    def test_links_present(self):
        response = self.client.get(reverse("exercises:choose_exercise"))
        self.assertContains(response, reverse("exercises:intervals_question"))
        self.assertContains(response, reverse("exercises:scale_degrees_question"))
