import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Tag, User
from src.repository.tags import create_tag, get_tag, get_tags, remove_tag, update_tag
from src.schemas import TagModel


class TestTags(unittest.IsolatedAsyncioTestCase):
    """Unit tests for tag repository operations."""

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_tags(self):
        tags = [Tag(id=1, name="work", user_id=1), Tag(id=2, name="home", user_id=1)]
        self.session.query().filter().offset().limit().all.return_value = tags

        result = await get_tags(skip=0, limit=10, user=self.user, db=self.session)

        self.assertEqual(result, tags)

    async def test_get_tag_found(self):
        tag = Tag(id=1, name="work", user_id=1)
        self.session.query().filter().first.return_value = tag

        result = await get_tag(tag_id=1, user=self.user, db=self.session)

        self.assertEqual(result, tag)

    async def test_get_tag_not_found(self):
        self.session.query().filter().first.return_value = None

        result = await get_tag(tag_id=1, user=self.user, db=self.session)

        self.assertIsNone(result)

    async def test_create_tag(self):
        body = TagModel(name="work")

        result = await create_tag(body=body, user=self.user, db=self.session)

        self.assertEqual(result.name, body.name)
        self.assertEqual(result.user_id, self.user.id)
        self.session.add.assert_called_once_with(result)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(result)

    async def test_update_tag_found(self):
        tag = Tag(id=1, name="old", user_id=1)
        self.session.query().filter().first.return_value = tag
        body = TagModel(name="new")

        result = await update_tag(tag_id=1, body=body, user=self.user, db=self.session)

        self.assertEqual(result, tag)
        self.assertEqual(tag.name, "new")
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(tag)

    async def test_update_tag_not_found(self):
        self.session.query().filter().first.return_value = None
        body = TagModel(name="new")

        result = await update_tag(tag_id=1, body=body, user=self.user, db=self.session)

        self.assertIsNone(result)
        self.session.commit.assert_not_called()

    async def test_remove_tag_found(self):
        tag = Tag(id=1, name="work", user_id=1)
        self.session.query().filter().first.return_value = tag

        result = await remove_tag(tag_id=1, user=self.user, db=self.session)

        self.assertEqual(result, tag)
        self.session.delete.assert_called_once_with(tag)
        self.session.commit.assert_called_once()

    async def test_remove_tag_not_found(self):
        self.session.query().filter().first.return_value = None

        result = await remove_tag(tag_id=1, user=self.user, db=self.session)

        self.assertIsNone(result)
        self.session.delete.assert_not_called()
        self.session.commit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
