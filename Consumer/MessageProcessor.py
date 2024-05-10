import xml.etree.ElementTree as ET
from datetime import datetime

class MessageProcessor:
    def process_message(self, xml_data):
        root = ET.fromstring(xml_data)
        message_dict = {child.tag: child.text for child in root.iter()}
        message_dict["Timestamp"] = datetime.utcnow().isoformat() + 'Z'
        return message_dict
