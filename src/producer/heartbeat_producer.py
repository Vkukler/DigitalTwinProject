import time
from config import settings
from .base_producer import BaseProducer

class HeartbeatProducer(BaseProducer):
    def run(self):
        try:
            with open(settings.CSV_FILE_PATH, "r") as file:
                for line in file:
                    try:
                        id, timestamp_str, heartbeat_str = line.strip().split(",")
                        heartbeat_value = int(heartbeat_str)

                        heartbeat_data = {
                            "userId": settings.USER_ID,
                            "heartbeat": heartbeat_value,
                            "timestamp": timestamp_str,
                        }
                        self.publisher.publish(settings.HEARTBEAT_QUEUE, heartbeat_data)
                        time.sleep(10)

                    except (ValueError, IndexError):
                        print(f" [!] Skipping invalid line: {line.strip()}")

        except FileNotFoundError:
            print(f" [!] File not found: {settings.CSV_FILE_PATH}")
