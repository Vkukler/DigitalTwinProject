import threading
import time
import json
from config import settings
from producer.publisher import RabbitMQPublisher


class BaseProducer:
    def __init__(self, *, queue_name, signal_name, csv_file_path, interval, user_id=None, event_type="measurement"):
        self.queue_name = queue_name
        self.signal_name = signal_name
        self.csv_file_path = csv_file_path
        self.interval = interval
        self.user_id = user_id or settings.USER_ID
        self.event_type = event_type  # default: measurement

    def run(self):

        publisher = RabbitMQPublisher(self.queue_name)

        try:
            with open(self.csv_file_path, "r") as file:
                for line in file:
                    try:
                        id, timestamp_str, value = line.strip().split(",")
                        value = float(value)

                        event = {
                            "device_id": self.user_id,
                            "timestamp": str(timestamp_str),
                            "type": self.event_type,        # measurement
                            "signal": self.signal_name,     # e.g. "calories"
                            "value": value
                        }

                        publisher.publish(event)
                        time.sleep(self.interval)

                    except (ValueError, IndexError):
                        print(f" [!] Skipping invalid line: {line.strip()}")

        except FileNotFoundError:
            print(f" [!] File not found: {self.csv_file_path}")
        finally:
            publisher.close()

    def start(self):
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return thread

