import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from src.database.models import User
from src.repository.users import (
    confirmed_email,
    create_user,
    get_user_by_email,
    update_avatar,
    update_token,
)
from src.schemas import UserModel


class TestUsers(unittest.IsolatedAsyncioTestCase):
    """Unit tests for user repository operations."""

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(
            id=1,
            username="test_user",
            email="test@example.com",
            password="hashed-password",
        )

    async def test_get_user_by_email_found(self):
        self.session.query().filter().first.return_value = self.user

        result = await get_user_by_email(email=self.user.email, db=self.session)

        self.assertEqual(result, self.user)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None

        result = await get_user_by_email(email="missing@example.com", db=self.session)

        self.assertIsNone(result)

    @patch("src.repository.users.Gravatar")
    async def test_create_user(self, mock_gravatar):
        avatar_url = "https://example.com/avatar.png"
        mock_gravatar.return_value.get_image.return_value = avatar_url
        body = UserModel(
            username="new_user",
            email="new@example.com",
            password="hashed-password",
        )

        result = await create_user(body=body, db=self.session)

        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertEqual(result.avatar, avatar_url)
        self.session.add.assert_called_once_with(result)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(result)

    async def test_update_token(self):
        token = "refresh-token"

        result = await update_token(user=self.user, token=token, db=self.session)

        self.assertIsNone(result)
        self.assertEqual(self.user.refresh_token, token)
        self.session.commit.assert_called_once()

    async def test_confirmed_email_found(self):
        self.session.query().filter().first.return_value = self.user

        result = await confirmed_email(email=self.user.email, db=self.session)

        self.assertIsNone(result)
        self.assertTrue(self.user.confirmed)
        self.session.commit.assert_called_once()

    async def test_confirmed_email_not_found(self):
        self.session.query().filter().first.return_value = None

        result = await confirmed_email(email="missing@example.com", db=self.session)

        self.assertIsNone(result)
        self.session.commit.assert_not_called()

    async def test_update_avatar_found(self):
        avatar_url = "https://example.com/avatar.png"
        self.session.query().filter().first.return_value = self.user

        result = await update_avatar(email=self.user.email, url=avatar_url, db=self.session)

        self.assertEqual(result, self.user)
        self.assertEqual(self.user.avatar, avatar_url)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(self.user)

    async def test_update_avatar_not_found(self):
        self.session.query().filter().first.return_value = None

        result = await update_avatar(
            email="missing@example.com",
            url="https://example.com/avatar.png",
            db=self.session,
        )

        self.assertIsNone(result)
        self.session.commit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
