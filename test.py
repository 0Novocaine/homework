from mongoengine import connect
from models import Contact

connect(db='contacts_db', host='mongodb://localhost:27017/contacts_db')
for user in Contact.objects:
    print(user.full_name, user.email, user.message_sent)