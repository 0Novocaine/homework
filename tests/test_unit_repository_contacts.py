import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.repository.contacts import (
    create_contact,
    get_contact,
    get_contacts,
    get_upcoming_birthdays,
    remove_contact,
    search_contacts,
    update_contact,
)
from src.schemas import ContactCreate, ContactUpdate


class TestContacts(unittest.TestCase):
    """Unit tests for contact repository operations."""

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.body = ContactCreate(
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            phone="+380991234567",
            birthday=date(1990, 6, 15),
            additional_data="Friend",
        )

    def test_get_contacts(self):
        contacts = [Contact(id=1), Contact(id=2)]
        self.session.query().filter().offset().limit().all.return_value = contacts

        result = get_contacts(skip=0, limit=10, user=self.user, db=self.session)

        self.assertEqual(result, contacts)

    def test_get_contact_found(self):
        contact = Contact(id=1, user_id=self.user.id)
        self.session.query().filter().first.return_value = contact

        result = get_contact(contact_id=1, user=self.user, db=self.session)

        self.assertEqual(result, contact)

    def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None

        result = get_contact(contact_id=1, user=self.user, db=self.session)

        self.assertIsNone(result)

    def test_search_contacts(self):
        contacts = [Contact(id=1, first_name="Jane")]
        self.session.query().filter().offset().limit().all.return_value = contacts

        result = search_contacts(query="jane", skip=0, limit=10, user=self.user, db=self.session)

        self.assertEqual(result, contacts)

    def test_create_contact(self):
        result = create_contact(body=self.body, user=self.user, db=self.session)

        self.assertEqual(result.first_name, self.body.first_name)
        self.assertEqual(result.email, self.body.email)
        self.assertEqual(result.user, self.user)
        self.session.add.assert_called_once_with(result)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(result)

    def test_update_contact_found(self):
        contact = Contact(id=1, first_name="Old", user_id=self.user.id)
        updated_body = ContactUpdate(
            first_name="Jane",
            last_name="Doe",
            email="updated@example.com",
            phone="+380991234567",
            birthday=date(1990, 6, 15),
            additional_data="Updated",
        )
        self.session.query().filter().first.return_value = contact

        result = update_contact(contact_id=1, body=updated_body, user=self.user, db=self.session)

        self.assertEqual(result, contact)
        self.assertEqual(contact.first_name, "Jane")
        self.assertEqual(contact.email, "updated@example.com")
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(contact)

    def test_update_contact_not_found(self):
        self.session.query().filter().first.return_value = None

        result = update_contact(contact_id=1, body=self.body, user=self.user, db=self.session)

        self.assertIsNone(result)
        self.session.commit.assert_not_called()

    def test_remove_contact_found(self):
        contact = Contact(id=1, user_id=self.user.id)
        self.session.query().filter().first.return_value = contact

        result = remove_contact(contact_id=1, user=self.user, db=self.session)

        self.assertEqual(result, contact)
        self.session.delete.assert_called_once_with(contact)
        self.session.commit.assert_called_once()

    def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None

        result = remove_contact(contact_id=1, user=self.user, db=self.session)

        self.assertIsNone(result)
        self.session.delete.assert_not_called()
        self.session.commit.assert_not_called()

    def test_get_upcoming_birthdays(self):
        today = date.today()
        upcoming = Contact(birthday=today + timedelta(days=2))
        later = Contact(birthday=today + timedelta(days=8))
        self.session.query().filter().all.return_value = [upcoming, later]

        result = get_upcoming_birthdays(days=7, user=self.user, db=self.session)

        self.assertEqual(result, [upcoming])


if __name__ == "__main__":
    unittest.main()
