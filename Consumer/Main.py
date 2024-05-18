import sys
import time
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from ConnectionManager import ConnectionManager
from MessageProcessor import MessageProcessor
from HeartbeatChecker import HeartbeatChecker
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SystemMonitor:
    def __init__(self, list_of_systems):
        self.connection_manager = ConnectionManager("rabbitmq", 5672, "user", "password")
        self.message_processor = MessageProcessor()
        self.heartbeat_checker = HeartbeatChecker(list_of_systems, self)
        self.session = self.create_http_session()

    def create_http_session(self):
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def send_to_logstash(self, system_data):
        headers = {"Content-type": "application/json"}
        try:
            response = self.session.post("http://logstash:8095", json=system_data, headers=headers)
            if response.status_code == 200:
                logging.info(f"Data sent to Logstash successfully: {system_data}")
            else:
                logging.error(f"Failed to send data to Logstash: {response.status_code} - {response.text}\nData: {system_data}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending data to Logstash: {e}\nData: {system_data}", exc_info=True)

    def send_to_http_endpoint(self, system_data):
        headers = {"Content-type": "application/json"}
        try:
            response = self.session.post("http://logstash:8097", json=system_data, headers=headers)
            if response.status_code == 200:
                logging.info(f"Data sent to HTTP endpoint successfully: {system_data}")
            else:
                logging.error(f"Failed to send data to HTTP endpoint: {response.status_code} - {response.text}\nData: {system_data}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending data to HTTP endpoint: {e}\nData: {system_data}", exc_info=True)

    def handle_message(self, ch, method, properties, body):
        system_data = self.message_processor.process_message(body)
        current_time = time.time()
        formatted_time = datetime.utcfromtimestamp(current_time).isoformat() + 'Z'

        need_send, is_active, interval = self.heartbeat_checker.check_system_active(system_data["SystemName"], current_time)

        json_data = {
            "Timestamp": formatted_time,
            "SystemName": system_data["SystemName"],
            "Status": "Active" if is_active else "Down",
            "Heartbeat-Interval": interval
        }

        if need_send:
            try:
                logging.info(f"Processed message: {json_data}")
                self.send_to_logstash(json_data)
            except Exception as e:
                logging.error(f"Error handling message: {e}", exc_info=True)

    def send_constant_status(self):
        while True:
            current_time = time.time()
            for system_name, last_time in self.heartbeat_checker.last_heartbeat.items():
                formatted_time = datetime.utcfromtimestamp(current_time).isoformat() + 'Z'
                is_active = self.heartbeat_checker.system_state.get(system_name, False)
                interval = current_time - last_time if last_time else 0
                json_data = {
                    "Timestamp": formatted_time,
                    "SystemName": system_name,
                    "Status": "Active" if is_active else "Down",
                    "Heartbeat-Interval": interval
                }
                self.send_to_http_endpoint(json_data)
            time.sleep(1)

    def consume_heartbeat_messages(self):
        connection = self.connection_manager.create_connection()
        channel = self.connection_manager.create_channel(connection)
        channel.basic_consume(queue='heartbeat_queue', on_message_callback=self.handle_message, auto_ack=True)
        logging.info("Start consuming heartbeat messages. To exit press CTRL+C")
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
            connection.close()
            sys.exit(0)
        except Exception as e:
            logging.error(f"Error in message consumption: {e}", exc_info=True)
            connection.close()
            sys.exit(1)

if __name__ == "__main__":
    list_of_systems = ['crm', 'frontend', 'kassa', 'ExampleSystem', 'facturatie', 'planning', 'mailing', 'inventree']
    system_monitor = SystemMonitor(list_of_systems)
    
    system_monitor.heartbeat_checker.start_monitoring()
    system_monitor.consume_heartbeat_messages()