from django.test import TestCase
from django.urls import reverse  


class SignUpViewTests(TestCase):
    def test_url_exists_at_correct_location(self):
        response = self.client.get("/accounts/signup/")
        self.assertEqual(response.status_code, 200)

    def test_url_available_by_name(self):  
        response = self.client.get(reverse("accounts:signup"))
        self.assertEqual(response.status_code, 200)

    def test_template_name_correct(self):  
        response = self.client.get(reverse("accounts:signup"))
        self.assertTemplateUsed(response, "registration/signup.html")
    
    def test_template_content(self):
        response = self.client.get(reverse("accounts:signup"))
        self.assertContains(response, "Log in")

    def test_user_can_sing_up(self):
        # user cannot log in because they don't have an account yet
        login = self.client.login(username="just_user123", password="Mf9rGyjAgMTA")
        self.assertFalse(login)
        # user signs up
        response = self.client.post(
            reverse("accounts:signup"), {
                "username": "just_user123",
                "password1": "Mf9rGyjAgMTA",
                "password2": "Mf9rGyjAgMTA",
            }
        )
        # user gets redirected to the login page
        self.assertRedirects(response, reverse('login'))
        # now user can log in
        login = self.client.login(username="just_user123", password="Mf9rGyjAgMTA")
        self.assertTrue(login)
