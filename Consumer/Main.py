import sys
import time
from datetime import datetime
import requests
from ConnectionManager import ConnectionManager
from MessageProcessor import MessageProcessor
from HeartbeatChecker import HeartbeatChecker

class SystemMonitor:
    def __init__(self, list_of_systems):
        self.connection_manager = ConnectionManager("rabbitmq", 5672, "user", "password")
        self.message_processor = MessageProcessor()
        self.heartbeat_checker = HeartbeatChecker(list_of_systems)

    def send_to_logstash(self, system_data):
        headers = {"Content-type": "application/json"}
        response = requests.post("http://logstash01:8095", json=system_data, headers=headers)
        print(f"Send status: {response.status_code} - {response.text}", f"Data: {system_data}")

    def handle_message(self, ch, method, properties, body):
        system_data = self.message_processor.process_message(body)
        current_time = time.time()  # Record the time the message was processed
        formatted_time = datetime.utcfromtimestamp(current_time).isoformat() + 'Z'

        is_active, interval = self.heartbeat_checker.check_system_active(system_data["SystemName"], current_time)

        json_data = {
            "Timestamp": formatted_time,
            "SystemName": system_data["SystemName"],
            "Status": "Active" if is_active else "Inactive",
            "Heartbeat-Interval": interval
        }

        print(json_data)

        self.send_to_logstash(json_data)

        if not is_active:
            error_xml = f'<ErrorLog><Timestamp>{current_time}</Timestamp><SystemName>{system_data["SystemName"]}</SystemName><Status>Down</Status><Interval>{interval}</Interval></ErrorLog>'
            self.connection_manager.send_xml_to_rabbitmq('mailing', system_data["SystemName"], error_xml)

    def consume_heartbeat_messages(self):
        connection = self.connection_manager.create_connection()
        channel = self.connection_manager.create_channel(connection)
        channel.basic_consume(queue='heartbeat_queue', on_message_callback=self.handle_message, auto_ack=True)
        print("Start consuming heartbeat messages. To exit press CTRL+C")
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
            connection.close()
            sys.exit(0)

if __name__ == "__main__":
    list_of_systems = ['crm', 'frontend', 'kassa', 'ExampleSystem', 'facturatie', 'planning', 'mailing', 'inventree']
    system_monitor = SystemMonitor(list_of_systems)
    
    system_monitor.heartbeat_checker.start_monitoring()

    system_monitor.consume_heartbeat_messages()
