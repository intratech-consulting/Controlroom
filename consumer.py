import pika 
import requests
import xml.etree.ElementTree as ET
import time
from datetime import datetime

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials('user', 'password')))
channel = connection.channel()

queue_name = "heartbeat_queue"

# parse XML and convert to dictionary/json
def xml_to_dict(xml_data):
    tree = ET.ElementTree(ET.fromstring(xml_data))
    root = tree.getroot()
    data = {child.tag: child.text for child in root}
    return data

# Function to check and update the status
def update_status(system_name, last_message_times):
    if time.time() - last_message_times[system_name]['time'] > 10:
        if last_message_times[system_name]['status'] == 'Active':
            last_message_times[system_name]['status'] = 'Inactive'
            return 'Inactive'
    else:
        if last_message_times[system_name]['status'] == 'Inactive':
            last_message_times[system_name]['status'] = 'Active'
            return 'Active'
    return last_message_times[system_name]['status']

# Function to calculate the interval between two timestamps
def calculate_time_difference(system_name, timestamp, last_message_times):
    if system_name in last_message_times:
        last_timestamp = last_message_times[system_name].get('timestamp')
        if last_timestamp:
            last_time = datetime.fromisoformat(last_timestamp)
            current_time = datetime.fromisoformat(timestamp)
            difference = (current_time - last_time).total_seconds()
            return difference
    return None

# Function to process messages
def process_message(body, last_message_times):
    dict_data = xml_to_dict(body.decode("utf-8"))
    system_name = dict_data.get('SystemName', 'Unknown')
    timestamp = dict_data.get('Timestamp')
             
    # Calculate the time difference and add it to the JSON dictionary
    time_difference = calculate_time_difference(system_name, timestamp, last_message_times)
    if time_difference is not None:
        dict_data['TimeDifference'] = time_difference

    # Update last message time for the system
    last_message_times.setdefault(system_name, {'time': time.time(), 'status': 'Active', 'timestamp': None})
    last_message_times[system_name]['time'] = time.time()
    last_message_times[system_name]['timestamp'] = timestamp

    # Check and update the status
    dict_data['Status'] = update_status(system_name, last_message_times)

    return dict_data

# Callback function to handle incoming messages from RabbitMQ
def callback(ch, method, properties, body):
    print("received %r" % body)
    headers = {'Content-type': 'application/json'}
    dict_data = process_message(body, callback.last_message_times)
    response = requests.post('http://localhost:8080', json=dict_data, headers=headers)
    print('Response: %s - %s' % (response.status_code, response.reason))
    print("xml to json: ", dict_data)

# Initialization of last message timestamps
callback.last_message_times = {}

channel.basic_consume(
    queue=queue_name, 
    on_message_callback=callback, 
    auto_ack=True
)

print("Waiting for messages. To exit press CTRL+C")
channel.start_consuming()
