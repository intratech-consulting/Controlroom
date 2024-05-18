import pika
import logging
from MessageProcessor import MessageProcessor
from LogstashSender import LogstashSender

class RabbitMQConsumer:
    def __init__(self, queue_name):
        self.queue_name = queue_name
        self.connection_params = pika.ConnectionParameters(
            'rabbitmq', 5672, '/', pika.PlainCredentials('user', 'password')
        )

    def on_message_received(self, channel, method_frame, header_frame, body):
        try:
            logging.info(f"Received message: {body}")
            json_data = MessageProcessor.xml_to_json(body.decode())
            logging.info(f"Converted JSON: {json_data}")
            if LogstashSender.send_to_logstash(json_data):
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            else:
                channel.basic_nack(delivery_tag=method_frame.delivery_tag)
        except Exception as e:
            logging.error(f"Error processing message: {e}", exc_info=True)
            channel.basic_nack(delivery_tag=method_frame.delivery_tag)

    def start_consuming(self):
        try:
            connection = pika.BlockingConnection(self.connection_params)
            logging.info("Connected to RabbitMQ")
            channel = connection.channel()
            
            channel.queue_declare(queue=self.queue_name, durable=True)
            channel.basic_consume(self.queue_name, on_message_callback=self.on_message_received, auto_ack=False)
            
            logging.info("Starting to consume from RabbitMQ...")
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError as e:
            logging.error(f"Failed to connect to RabbitMQ: {e}", exc_info=True)
        except KeyboardInterrupt:
            logging.info("Consumer stopped.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}", exc_info=True)
        finally:
            try:
                connection.close()
                logging.info("Connection closed")
            except Exception as e:
                logging.error(f"Error closing connection: {e}", exc_info=True)
