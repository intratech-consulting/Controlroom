import pika
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def xml_to_json(xml_data):
    """Convert XML data to JSON format, handling cases where elements may be missing."""
    root = ET.fromstring(xml_data)
    
    # Safely access elements, defaulting to None or an appropriate default if not found.
    system_name = root.find('SystemName').text if root.find('SystemName') is not None else None
    function_name = root.find('FunctionName').text if root.find('FunctionName') is not None else None
    logs = root.find('Logs').text if root.find('Logs') is not None else None
    error = root.find('Error').text == 'true' if root.find('Error') is not None else False
    timestamp = root.find('Timestamp').text if root.find('Timestamp') is not None else None
    
    # Construct JSON object
    json_data = {
        "SystemName": system_name,
        "FunctionName": function_name,
        "Logs": logs,
        "Error": error,
        "Timestamp": timestamp
    }
    
    return json_data

def on_message_received(channel, method_frame, header_frame, body):
    try:
        headers = {"Content-type": "application/json"}
        logging.info(f"Received message: {body}")
        json_data = xml_to_json(body.decode())
        logging.info(f"Converted JSON: {json.dumps(json_data, indent=2)}")
        response = requests.post('http://logstash:8096', json=json_data, headers=headers)
        if response.status_code == 200:
            logging.info("Successfully sent message to Logstash.")
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        else:
            logging.error(f"Failed to send message to Logstash: {response.status_code} - {response.text}")
            channel.basic_nack(delivery_tag=method_frame.delivery_tag)
    except Exception as e:
        logging.error(f"Error processing message: {e}", exc_info=True)
        channel.basic_nack(delivery_tag=method_frame.delivery_tag)

def main():
    connection_params = pika.ConnectionParameters('rabbitmq', 5672, '/', pika.PlainCredentials('user', 'password'))
    try:
        connection = pika.BlockingConnection(connection_params)
        logging.info("Connected to RabbitMQ")
        channel = connection.channel()
        
        channel.queue_declare(queue='Loggin_queue', durable=True)
        channel.basic_consume('Loggin_queue', on_message_callback=on_message_received, auto_ack=False)
        
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

if __name__ == '__main__':
    main()
