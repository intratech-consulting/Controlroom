import threading
import time
from datetime import datetime
import logging
import sys
from MessageProcessor import MessageProcessor

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,  # You can adjust the level to INFO or ERROR as needed
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class HeartbeatChecker:
    def __init__(self, list_of_systems, monitor):
        self.last_heartbeat = {system: None for system in list_of_systems}
        self.system_state = {system: True for system in list_of_systems}
        self.system_down_time = {system: None for system in list_of_systems}  # Store the time when a system went down
        self.system_monitor = monitor
        self.xml_data = """
        <Heartbeat>
            <Timestamp>{timestamp}</Timestamp>
            <Status>Inactive</Status>
            <SystemName>{system_name}</SystemName>
        </Heartbeat>
        """
        
        self.xsd_data = """
        <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
            <xs:element name="Heartbeat">
                <xs:complexType>
                    <xs:sequence>
                        <xs:element name="Timestamp" type="xs:dateTime" />
                        <xs:element name="Status" type="xs:string" />
                        <xs:element name="SystemName" type="xs:string" />
                    </xs:sequence>
                </xs:complexType>
            </xs:element>
        </xs:schema>
        """
        self.message_processor = MessageProcessor()
    
    def start_monitoring(self):
        self.monitoring_thread = threading.Thread(target=self.run_monitoring)
        self.monitoring_thread.start()
        # Start a new thread to send constant status updates
        self.status_thread = threading.Thread(target=self.system_monitor.send_constant_status)
        self.status_thread.start()
    
    def run_monitoring(self):
        while True:
            logging.error(f"\n\n\n\n\n\nLaunching the thread\n\n\n\n\n\n")            
            try:
                self.check_systems_active()
                time.sleep(5)  # Sleep for 5 seconds between checks
            except Exception as e:
                logging.error(f"\n\n\n\n\n\nError during system check: {e}\n\n\n\n\n\n")

    def check_systems_active(self):
        # Record the current time as a timestamp
        current_time = time.time()

        logging.error("\n\n\n\n\n\n\n\n\n\nchecking systems\n\n\n\n\n\n\n\n\n\n")
        
        for system_name in self.last_heartbeat.keys():
            if self.last_heartbeat[system_name] is not None:
                # Calculate the interval using timestamps
                interval = current_time - self.last_heartbeat[system_name]
                if interval >= 5 and self.system_state[system_name] is not False:
                    self.system_state[system_name] = False  # Mark the system as inactive due to timeout
                    logging.error(f"\n\n\n\n\n\n\n\n\n\System {system_name} marked inactive due to no heartbeat for 5 seconds.n\n\n\n\n\n\n\n\n\n\n")
                    timestamp = datetime.utcfromtimestamp(current_time).isoformat()
                    formatted_xml_data = self.xml_data.format(timestamp=timestamp, system_name=system_name)
                    self.message_processor.validate_and_send_xml(formatted_xml_data, self.xsd_data)
                    json_data = {
                        "Timestamp": timestamp,
                        "SystemName": system_name,
                        "Status": "Down",
                        "Heartbeat-Interval": interval
                    }
                    self.system_monitor.send_to_logstash(json_data)

            elif self.last_heartbeat[system_name] is None:
                self.system_state[system_name] = None  # Still no heartbeat received

    def check_system_active(self, system_name, current_time):
        last_time = self.last_heartbeat.get(system_name)
        interval = 0
        if last_time is not None:
            interval = current_time - last_time
            if interval >= 5:
                # If the interval is greater than 5 seconds, consider the system inactive.
                if self.system_state[system_name]:
                    self.system_state[system_name] = False
                    self.system_down_time[system_name] = last_time  # Mark the time the system went down
                    self.last_heartbeat[system_name] = current_time
                    return True, False, -1
                else:
                    if self.system_down_time[system_name] is not None:
                        downtime = self.last_heartbeat[system_name] - self.system_down_time[system_name]
                    else:
                        downtime = interval  # Treat as no downtime recorded yet

                    self.last_heartbeat[system_name] = current_time
                    self.system_state[system_name] = True
                    self.system_down_time[system_name] = None
                    return True, True, downtime  # Indicating a reset

            else:
                # If interval < 5 seconds, and system was previously inactive
                if not self.system_state[system_name]:
                    if self.system_down_time[system_name] is not None:
                        downtime = current_time - self.system_down_time[system_name]
                    else:
                        downtime = interval  # No recorded down time
                        
                    self.system_state[system_name] = True  # Mark system as active
                    self.last_heartbeat[system_name] = current_time
                    return False, False, -3
        else:
            # First heartbeat, no last time available                
            self.last_heartbeat[system_name] = current_time
            return True, True, 0

        self.last_heartbeat[system_name] = current_time
        return False, True, -5
