from mongoengine import Document, StringField, EmailField, BooleanField, DateTimeField
import datetime

class Contact(Document):
    full_name = StringField(required=True)
    email = EmailField(required=True, unique=True)
    message_sent = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    note = StringField()