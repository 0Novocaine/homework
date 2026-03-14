import pika
import json
from faker import Faker
from mongoengine import connect
from models import Contact

connect(db='contacts_db', host='mongodb://localhost:27017/contacts_db')

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',
        port=5672,
        credentials=pika.PlainCredentials('admin', 'admin')
    )
)
channel = connection.channel()
channel.queue_declare(queue='email_queue')

fake = Faker()
NUM_CONTACTS = 10

for _ in range(NUM_CONTACTS):
    contact = Contact(
        full_name=fake.name(),
        email=fake.email(),
        note=fake.sentence()
    )
    contact.save()
    message = json.dumps({'contact_id': str(contact.id)})
    channel.basic_publish(exchange='', routing_key='email_queue', body=message)
    print(f"Sent to queue: {message}")

connection.close()
print("Producer finished sending messages.")