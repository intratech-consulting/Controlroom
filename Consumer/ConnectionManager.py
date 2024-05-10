import pika

class ConnectionManager:
    def __init__(self, host, port, username, password):
        self.parameters = pika.ConnectionParameters(
            host, port, "/", pika.PlainCredentials(username, password)
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
