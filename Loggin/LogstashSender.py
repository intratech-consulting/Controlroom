import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class LogstashSender:
    @staticmethod
    def send_to_logstash(json_data):
        headers = {"Content-type": "application/json"}
        logstash_url = os.getenv('LOGSTASH_URL_LOGGIN')
        try:
            response = requests.post(logstash_url, json=json_data, headers=headers)
            if response.status_code == 200:
                logging.info("Successfully sent message to Logstash.")
                return True
            else:
                logging.error(f"Failed to send message to Logstash: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logging.error(f"Error sending message to Logstash: {e}", exc_info=True)
            return False
