import pika

def callback(ch, method, properties, body):
    # Decode the message body from UTF-16
    xml_message = body.decode('utf-16')
    
    # Print the decoded XML message
    print(" [x] Received XML content:")
    print(xml_message)

# Establish connection to the local RabbitMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials('user', 'password')))
channel = connection.channel()

# Ensure the queue exists
channel.queue_declare(queue='xml_queue')

# Start consuming messages from the queue, using the callback to process messages
channel.basic_consume(queue='xml_queue',
                      auto_ack=True,
                      on_message_callback=callback)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
