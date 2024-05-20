import xml.etree.ElementTree as ET

class MessageProcessor:
    @staticmethod
    def xml_to_json(xml_data):
        """Convert XML data to JSON format, handling cases where elements may be missing."""
        root = ET.fromstring(xml_data)
        
        # Safely access elements, defaulting to None or an appropriate default if not found.
        system_name = root.find('SystemName').text if root.find('SystemName') is not None else None
        function_name = root.find('FunctionName').text if root.find('FunctionName') is not None else None
        logs = root.find('Logs').text if root.find('Logs') is not None else None
        
        error_text = root.find('Error').text if root.find('Error') is not None else "false"
        error = error_text.lower() in ["true", "1", "t", "yes"] if isinstance(error_text, str) else bool(error_text)
        
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
