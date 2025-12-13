from django.test import TestCase
from .models import CustomUser


class GoogleLoginFlagTests(TestCase):
	def test_google_login_flag_default_false(self):
		user = CustomUser.objects.create(username='testuser', email='test@example.com')
		self.assertFalse(user.google_login_enabled)

	def test_google_login_flag_can_be_set(self):
		user = CustomUser.objects.create(username='guser', email='guser@example.com', google_login_enabled=True)
		self.assertTrue(user.google_login_enabled)
