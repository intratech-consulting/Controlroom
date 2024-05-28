from lxml import etree as ET
from datetime import datetime
from ConnectionManager import ConnectionManager
import logging
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class MessageProcessor:
    
    def __init__(self):
        self.connection_manager = ConnectionManager()

    def process_message(self, xml_data):
        root = ET.fromstring(xml_data)
        message_dict = {child.tag: child.text for child in root.iter()}
        message_dict["Timestamp"] = datetime.utcnow().isoformat() + 'Z'
        return message_dict

    def validate_and_send_xml(self, xml_data, xsd_data):
        xsd_doc = ET.fromstring(xsd_data.encode())
        schema = ET.XMLSchema(xsd_doc)
            

        try:
            formatted_heartbeat_xml = xml_data.format(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f"))
            xml_doc = ET.fromstring(formatted_heartbeat_xml.encode())               

            if schema.validate(xml_doc):
                schema.error_log
                logging.info("************ XML VALID***********")
                self.connection_manager.send_xml_to_rabbitmq("amq.topic", "heartbeat", ET.tostring(xml_doc, encoding='utf8', method='xml'))
                logging.info("***********SENT XML***************")
            else:
                log = schema.error_log
                logging.info(f"\n\n\n\n\nXML NOT VALID: {log}\n\n\n\n\n")
        except Exception as e:
                logging.error(f"\n\n\n\n\n\nError XML SENDING: {e}\n\n\n\n\n\n")
