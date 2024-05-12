import pika
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

import xml.etree.ElementTree as ET

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
        print("Received message: %r" % body)
        json_data = xml_to_json(body.decode())
        print("Converted JSON:", json_data)
        response = requests.post('http://logstash:8096', json=json_data, headers=headers)
        if response.status_code == 200:
            print("Successfully sent message to Logstash.")
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        else:
            print("Failed to send message to Logstash:", response.text)
            channel.basic_nack(delivery_tag=method_frame.delivery_tag)
    except Exception as e:
        print("Error processing message:", e, "\n\n\n\n")
        channel.basic_nack(delivery_tag=method_frame.delivery_tag)


def main():
    connection_params = pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials('user', 'password'))
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    
    channel.queue_declare(queue='Loggin_queue', durable=True)
    channel.basic_consume('Loggin_queue', on_message_received, auto_ack=False)
    
    print("Starting to consume from RabbitMQ...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Consumer stopped.")
        connection.close()
        print("Connection closed")

if __name__ == '__main__':
    main()
