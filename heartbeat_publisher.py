import pika
import time
from xml.etree.ElementTree import Element, tostring

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials('user', 'password')))
channel = connection.channel()

# Declare a queue
channel.queue_declare(queue='heartbeat', durable=True)

while True:
    # Create an XML-formatted heartbeat message
    root = Element('Heartbeat')
    message_elem = Element('Message')
    message_elem.text = 'Hello World'
    root.append(message_elem)
    queue_elem = Element('Queue')
    queue_elem.text = 'heartbeat'
    root.append(queue_elem)

    message = tostring(root, encoding='unicode')
    channel.basic_publish(exchange='', routing_key='heartbeat', body=message)
    print(" [x] Sent 'Hello World' as XML")
    time.sleep(1)  # Adjust the timing as needed

connection.close()
