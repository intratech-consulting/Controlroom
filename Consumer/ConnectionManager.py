import pika
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class ConnectionManager:
    def __init__(self, host=None, port=None, username=None, password=None):
        self.parameters = pika.ConnectionParameters(
            host or os.getenv('RABBITMQ_HOST'),
            port or int(os.getenv('RABBITMQ_PORT')),
            "/",
            pika.PlainCredentials(
                username or os.getenv('RABBITMQ_USER'),
                password or os.getenv('RABBITMQ_PASSWORD')
            )
        )

    def create_connection(self):
        return pika.BlockingConnection(self.parameters)

    def create_channel(self, connection):
        return connection.channel()

    def send_xml_to_rabbitmq(self, exchange, routing_key, message):
        connection = self.create_connection()
        channel = self.create_channel(connection)
        channel.basic_publish(exchange=exchange, routing_key=routing_key, body=message)
        connection.close()
