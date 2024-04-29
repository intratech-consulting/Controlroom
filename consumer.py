import pika 
import requests
import xml.etree.ElementTree as ET
import time
from datetime import datetime

def create_connection():
    return pika.BlockingConnection(
        pika.ConnectionParameters(
            'rabbitmq',  # This should match the service name in docker-compose
            5672,
            '/',
            pika.PlainCredentials('user', 'password')
        )
    )

def create_channel(connection):
    return connection.channel()

def xml_to_dict(xml_data):
    tree = ET.ElementTree(ET.fromstring(xml_data))
    root = tree.getroot()
    return {child.tag: child.text for child in root}

def calculate_time_difference(system_name, timestamp, last_message_times):
    if system_name in last_message_times:
        last_timestamp = last_message_times[system_name].get('timestamp')
        if last_timestamp:
            last_time = datetime.fromisoformat(last_timestamp)
            current_time = datetime.fromisoformat(timestamp)
            return (current_time - last_time).total_seconds()
    return None

def process_message(body, last_message_times):
    dict_data = xml_to_dict(body.decode("utf-8"))
    system_name = dict_data.get('SystemName')
    timestamp = dict_data.get('Timestamp')
             
    time_difference = calculate_time_difference(system_name, timestamp, last_message_times)
    if time_difference is not None:
        dict_data['Heartbeat-Interval'] = time_difference
        dict_data['Status'] = 0 if time_difference >= 2 else 1

    last_message_times.setdefault(system_name, {'time': time.time(), 'timestamp': None})
    last_message_times[system_name]['time'] = time.time()
    last_message_times[system_name]['timestamp'] = timestamp

    return dict_data

def callback(ch, method, properties, body):
    print(f"------------------------------------")
    print(f"Received XML: {body}\n")
    headers = {'Content-type': 'application/json'}
    dict_data = process_message(body, callback.last_message_times)
    response = requests.post('http://logstash:8080', json=dict_data, headers=headers)
    print(f'Response Code: {response.status_code} - {response.reason} \n')
    print(f"XML to JSON: {dict_data} \n")
    print(f"------------------------------------\n")

def main():
    connection = create_connection()
    channel = create_channel(connection)
    callback.last_message_times = {}

    channel.basic_consume(
        queue="heartbeat_queue", 
        on_message_callback=callback, 
        auto_ack=True
    )

    print("Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == "__main__":
    main()

