import os
import threading
import time
import json
from pathlib import Path
from config import settings
from producer.publisher import RabbitMQPublisher


class BaseProducer:
    """
        Abstract base producer bound to one queue.
        Defines methods for:
        - Reading data
        - Encoding data
        - Publishing messages
    """
    def __init__(self, *, queue_name, signal_name, csv_file_path, interval, user_id=None, event_type="measurement"):
        self.queue_name = queue_name
        self.signal_name = signal_name
        self.csv_file_path = csv_file_path
        self.interval = interval
        self.user_id = user_id or settings.USER_ID
        self.event_type = event_type  # default: measurement

    def _offset_file(self):
        state_dir = Path(os.getenv("PRODUCER_STATE_DIR", "docs/influx/producer_offsets"))
        state_dir.mkdir(parents=True, exist_ok=True)
        return state_dir / f"{self.queue_name}.offset"

    def _read_offset(self, offset_file):
        try:
            return int(offset_file.read_text().strip())
        except (FileNotFoundError, ValueError):
            return 0

    def _write_offset(self, offset_file, line_number):
        offset_file.write_text(str(line_number))

    def run(self):

        publisher = RabbitMQPublisher(self.queue_name)
        offset_file = self._offset_file()
        next_line = self._read_offset(offset_file)

        try:
            with open(self.csv_file_path, "r") as file:
                for line_number, line in enumerate(file):
                    if line_number < next_line:
                        continue

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
                        self._write_offset(offset_file, line_number + 1)
                        time.sleep(self.interval)

                    except (ValueError, IndexError):
                        print(f" [!] Skipping invalid line: {line.strip()}")
                        self._write_offset(offset_file, line_number + 1)

        except FileNotFoundError:
            print(f" [!] File not found: {self.csv_file_path}")
        finally:
            publisher.close()

    def start(self):
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return thread
