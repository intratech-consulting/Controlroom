import threading
import time
import xml.etree.ElementTree as ET
from datetime import datetime
import pika
import requests

class SystemMonitor:
    list_of_systems = [
        "crm",
        "frontend",
        "kassa",
        "ExampleSystem",
        "facturatie",
        "planning",
        "mailing",
        "inventree",
    ]

    Mail_state = {
        'crm': True,
        'frontend': True,
        'kassa': True,
        'ExampleSystem': True,
        'facturatie': True,
        'planning': True,
        'mailing': True,
        'inventree': True
    }
    
    last_message_times = {}
    def create_connection(self):
        return pika.BlockingConnection(
            pika.ConnectionParameters(
                "rabbitmq", 5672, "/", pika.PlainCredentials("user", "password")
            )
        )
    def create_channel(self, connection):
        return connection.channel()
    def xml_to_dict(self, xml_data):
        tree = ET.ElementTree(ET.fromstring(xml_data))
        root = tree.getroot()
        return {child.tag: child.text for child in root}
    def calculate_time_difference(self, system_name, timestamp, last_message_times):
        if system_name in last_message_times:
            last_timestamp = last_message_times[system_name].get("timestamp")
            if last_timestamp:
                last_time = datetime.fromisoformat(last_timestamp)
                current_time = datetime.fromisoformat(timestamp)
                return (current_time - last_time).total_seconds()
        return None
    def process_message(self, body, last_message_times):
        dict_data = self.xml_to_dict(body.decode("utf-8"))
        system_name = dict_data.get("SystemName")
        timestamp = dict_data.get("Timestamp")
        time_difference = self.calculate_time_difference(
            system_name, timestamp, last_message_times
        )
        if time_difference is not None:
            dict_data["Heartbeat-Interval"] = time_difference
            if time_difference >= 5:
                dict_data["Status"] = 0

                if SystemMonitor.Mail_state[system_name]:
                    error_xml = f'<ErrorLog>\n\t<Timestamp>{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}</Timestamp>\n\t<Status>0</Status>\n\t<SystemName>{system_name}</SystemName></ErrorLog>'
                    self.send_to_mailing(error_xml)
                    SystemMonitor.Mail_state[system_name] = False
            else:
                dict_data["Status"] = 1
                SystemMonitor.Mail_state[system_name] = True
        last_message_times.setdefault(
            system_name, {"time": time.time(), "timestamp": None}
        )
        last_message_times[system_name]["time"] = time.time()
        last_message_times[system_name]["timestamp"] = timestamp
        return dict_data
    def callback(self, ch, method, properties, body):
        print(f"------------------------------------")
        print(f"Received XML: {body}\n")
        headers = {"Content-type": "application/json"}
        dict_data = self.process_message(body, SystemMonitor.last_message_times)
        response = requests.post(
            "http://logstash01:8090", json=dict_data, headers=headers
        )
        print(f"Response Code: {response.status_code} - {response.reason} \n")
        print(f"XML to JSON: {dict_data} \n")
        print(f"------------------------------------\n")
    def check_systems(self):
        while True:
            for system in SystemMonitor.list_of_systems:
                if (
                    system not in SystemMonitor.last_message_times
                    or time.time() - SystemMonitor.last_message_times[system]["time"]
                    >= 5
                ):
                    interval = (
                        time.time() - SystemMonitor.last_message_times[system]["time"]
                        if system in SystemMonitor.last_message_times
                        else 0
                    )
                    dict_data = {
                        "Timestamp": time.time(),
                        "SystemName": system,
                        "Status": 0,
                        "Heartbeat-Interval": interval,
                    }
                    headers = {"Content-type": "application/json"}
                    response = requests.post(
                        "http://logstash01:8090", json=dict_data, headers=headers
                    )
                    print(
                        f"Send System Down status: {response.status_code} - {response.reason}",
                        f"SystemName: {system}, Interval: {interval}",
                    )
                else:
                    interval = (
                        time.time() - SystemMonitor.last_message_times[system]["time"]
                    )
                    print("System up ->", f"SystemName: {system}, Interval: {interval}")
            time.sleep(5)
    def send_to_rabbitmq(self, message):
        connection = self.create_connection()
        channel = self.create_channel(connection)
        channel.basic_publish(exchange="topic", routing_key="heartbeat", body=message)
        connection.close()

    def send_to_mailing(self, message):
        connection = self.create_connection()
        channel = self.create_channel(connection)
        channel.basic_publish(exchange='topic', routing_key='mailing', body=message)
        connection.close()

    def main(self):
        connection = self.create_connection()
        channel = self.create_channel(connection)
        channel.basic_consume(
            queue="heartbeat_queue", on_message_callback=self.callback, auto_ack=True
        )
        heartbeat_check = threading.Thread(target=self.check_systems)
        heartbeat_check.start()
        print("Waiting for messages. To exit press CTRL+C")
        channel.start_consuming()

if __name__ == "__main__":
    system_monitor = SystemMonitor()
    system_monitor.main()