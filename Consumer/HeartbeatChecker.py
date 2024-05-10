import threading
import time
from datetime import datetime
import logging
import sys

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,  # You can adjust the level to INFO or ERROR as needed
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class HeartbeatChecker:
    def __init__(self, list_of_systems):
        self.last_heartbeat = {system: None for system in list_of_systems}
        self.system_state = {system: True for system in list_of_systems}
        self.system_down_time = {system: None for system in list_of_systems}  # Store the time when a system went down
    
    
    def start_monitoring(self):
        self.monitoring_thread = threading.Thread(target=self.run_monitoring)
        self.monitoring_thread.start()
    
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

        # Convert current time to string just for logging
        time_string = datetime.utcfromtimestamp(current_time).isoformat() + 'Z'
        logging.error("\n\n\n\n\n\n\n\n\n\nchecking systems\n\n\n\n\n\n\n\n\n\n")
        
        for system_name in self.last_heartbeat.keys():
            if self.last_heartbeat[system_name] is not None:
                # Calculate the interval using timestamps
                interval = current_time - self.last_heartbeat[system_name]
                if interval >= 5 and self.system_state[system_name] is not False:
                    self.system_state[system_name] = False  # Mark the system as inactive due to timeout
                    logging.error(f"\n\n\n\n\n\n\n\n\n\System {system_name} marked inactive due to no heartbeat for 5 seconds.n\n\n\n\n\n\n\n\n\n\n")
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
                    return False, interval
                else:
                    if self.system_down_time[system_name] is not None:
                        downtime = current_time - self.system_down_time[system_name]
                    else:
                        downtime = 0  # Treat as no downtime recorded yet
                        
                    if downtime > 1:  # Check if downtime criteria are met
                        self.last_heartbeat[system_name] = current_time
                        self.system_state[system_name] = None
                        self.system_down_time[system_name] = None
                        return True, -1  # Indicating a reset
                    return False, downtime
            else:
                # If interval < 5 seconds, and system was previously inactive
                if not self.system_state[system_name]:
                    if self.system_down_time[system_name] is not None:
                        downtime = current_time - self.system_down_time[system_name]
                    else:
                        downtime = 0  # No recorded down time
                        
                    self.system_state[system_name] = True  # Mark system as active
                    self.last_heartbeat[system_name] = current_time
                    return True, downtime
        else:
            # First heartbeat, no last time available
            self.last_heartbeat[system_name] = current_time
                
        self.last_heartbeat[system_name] = current_time
        return True, interval

