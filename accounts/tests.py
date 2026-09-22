from django.test import TestCase
from .forms import RegisterForm


class RegisterFormTests(TestCase):
	def test_password_can_match_username(self):
		form = RegisterForm(data={
			'username': 'pattern_user',
			'first_name': 'Pattern',
			'last_name': 'User',
			'email': 'pattern@example.com',
			'password1': 'pattern_user',
			'password2': 'pattern_user',
		})

		self.assertTrue(form.is_valid())

	def test_password_confirmation_is_still_required(self):
		form = RegisterForm(data={
			'username': 'new_user',
			'first_name': 'New',
			'last_name': 'User',
			'email': 'new@example.com',
			'password1': 'chosen-password',
			'password2': 'different-password',
		})

		self.assertFalse(form.is_valid())
		self.assertIn('password2', form.errors)
