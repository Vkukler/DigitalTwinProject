import threading
import time
import json
from config import settings


class BaseProducer:
    def __init__(self, publisher, *, queue_name, signal_name, csv_file_path, interval, user_id=None, event_type="measurement"):
        self.publisher = publisher
        self.queue_name = queue_name
        self.signal_name = signal_name
        self.csv_file_path = csv_file_path
        self.interval = interval
        self.user_id = user_id or settings.USER_ID
        self.event_type = event_type  # default: measurement

    def run(self):
        try:
            with open(self.csv_file_path, "r") as file:
                for line in file:
                    try:
                        id, timestamp_str, value = line.strip().split(",")
                        value = float(value)

                        event = {
                            "device_id": self.user_id,
                            "timestamp": int(timestamp_str),
                            "type": self.event_type,        # measurement
                            "signal": self.signal_name,     # e.g. "calories"
                            "value": value
                        }

                        self.publisher.publish(self.queue_name, event)
                        time.sleep(self.interval)

                    except (ValueError, IndexError):
                        print(f" [!] Skipping invalid line: {line.strip()}")

        except FileNotFoundError:
            print(f" [!] File not found: {self.csv_file_path}")

    def start(self):
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return thread

