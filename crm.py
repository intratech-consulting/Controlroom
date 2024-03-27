import pika
import time
import json  # Import the json module

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials('user', 'password')))
channel = connection.channel()

# Declare a queue
channel.queue_declare(queue='CRM', durable=True)

while True:
    # Send a JSON-formatted heartbeat message
    message = json.dumps({"message": "up and running (crm btw)", "queue": "CRM"})
    channel.basic_publish(exchange='', routing_key='CRM', body=message)
    print("I'm up and running! (crm btw)")
    time.sleep(1)  # Adjust the timing as needed

connection.close()
