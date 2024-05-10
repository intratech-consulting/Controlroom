import pika
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

class LoggingMonitor:
    def __init__(self, rabbitmq_server, logstash_endpoint):
        self.rabbitmq_server = rabbitmq_server
        self.logstash_endpoint = logstash_endpoint

    def create_connection(self):
        return pika.BlockingConnection(
            pika.ConnectionParameters(
                self.rabbitmq_server, 5672, "/", pika.PlainCredentials("user", "password")
            )
        )

    def xml_to_json(self, xml_data):
        """Converts XML data to a JSON-compatible dictionary."""
        root = ET.fromstring(xml_data)
        return {child.tag: child.text for child in root}

    def callback(self, ch, method, properties, body):
        """Handles incoming messages by converting them to JSON and forwarding them to Logstash."""
        print(f"Received XML: {body.decode()}")
        json_data = self.xml_to_json(body.decode())

        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(self.logstash_endpoint, json=json_data, headers=headers)
            print(f"Message forwarded to Logstash: {response.status_code} - {response.reason}")

            if response.status_code == 200:
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        except requests.exceptions.RequestException as e:
            print(f"Failed to send message to Logstash: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def consume(self):
        """Sets up RabbitMQ connection and message consumption."""
        connection = self.create_connection()
        channel = connection.channel()

        channel.queue_declare(queue='Loggin_queue', durable=True)
        channel.basic_consume(queue='Loggin_queue', on_message_callback=self.callback, auto_ack=False)

        print("Starting to consume from RabbitMQ...")
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            print("Consumer stopped.")
        finally:
            if connection.is_open:
                connection.close()
                print("Connection closed")

if __name__ == '__main__':
    logstash_url = "http://localhost:8096"  # Update this URL based on your actual Logstash HTTP input configuration
    rabbitmq_host = "localhost"
    monitor = LoggingMonitor(rabbitmq_host, logstash_url)
    monitor.consume()
