from .base_producer import BaseProducer
from .publisher import RabbitMQPublisher
from config import settings

class ProducerService:
    def __init__(self):
        self.publisher = RabbitMQPublisher()
        self.producers = []

        producer_configs = [
            {"queue": settings.HEARTRATE_QUEUE, "signal": "heart_rate",
             "file": settings.HEARTRATE_CSV_FILE_PATH, "interval": settings.HEARTRATE_INTERVAL},
            {"queue": settings.CALORIES_QUEUE, "signal": "calories",
             "file": settings.CALORIES_CSV_FILE_PATH, "interval": settings.CALORIES_INTERVAL},
        ]

        for cfg in producer_configs:
            producer = BaseProducer(
                publisher=self.publisher,
                queue_name=cfg["queue"],
                signal_name=cfg["signal"],
                csv_file_path=cfg["file"],
                interval=cfg["interval"]
            )
            self.producers.append(producer)

        self.threads = []

    def start(self):
        for p in self.producers:
            thread = p.start()
            self.threads.append(thread)
        print(f"[Replay App] Started {len(self.threads)} producers.")