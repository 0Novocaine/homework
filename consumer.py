import pika
import json
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

def send_email_stub(contact):
    print(f"Simulating sending email to {contact.email}")
    return True

def callback(ch, method, properties, body):
    data = json.loads(body)
    contact_id = data['contact_id']
    contact = Contact.objects(id=contact_id).first()
    if contact and not contact.message_sent:
        if send_email_stub(contact):
            contact.message_sent = True
            contact.save()
            print(f"Email sent to {contact.email}, marked as sent.")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue='email_queue', on_message_callback=callback)
print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()