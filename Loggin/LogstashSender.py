import requests
import logging

class LogstashSender:
    @staticmethod
    def send_to_logstash(json_data):
        headers = {"Content-type": "application/json"}
        try:
            response = requests.post('http://logstash:8096', json=json_data, headers=headers)
            if response.status_code == 200:
                logging.info("Successfully sent message to Logstash.")
                return True
            else:
                logging.error(f"Failed to send message to Logstash: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logging.error(f"Error sending message to Logstash: {e}", exc_info=True)
            return False
