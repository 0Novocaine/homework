from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PasswordResetTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='old-secure-password',
        )

    def test_password_reset_sends_a_one_time_link(self) -> None:
        response = self.client.post(
            reverse('fpq_user:password_reset'),
            {'email': self.user.email},
        )

        self.assertRedirects(response, reverse('fpq_user:password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('/user/reset-password/confirm/', mail.outbox[0].body)

    def test_password_can_be_changed_via_email_link(self) -> None:
        self.client.post(
            reverse('fpq_user:password_reset'),
            {'email': self.user.email},
        )
        reset_path = next(
            line for line in mail.outbox[0].body.splitlines()
            if '/user/reset-password/confirm/' in line
        )
        reset_path = reset_path.split('href="')[1].split('"')[0]
        reset_path = reset_path.replace('http://testserver', '')

        # Django validates the token first and redirects to a safe URL before
        # accepting a new password. This also prevents the token leaking in a
        # browser's Referer header.
        response = self.client.get(reset_path, follow=True)
        response = self.client.post(
            response.request['PATH_INFO'],
            {
                'new_password1': 'new-secure-password-123',
                'new_password2': 'new-secure-password-123',
            },
        )

        self.assertRedirects(response, reverse('fpq_user:password_reset_complete'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('new-secure-password-123'))
