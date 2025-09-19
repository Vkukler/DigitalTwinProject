from producer.base_producer import BaseProducer
from config import settings

class ProducerService:
    def __init__(self):
        self.producers = []

        producer_configs = [
            # heart rate
            {"queue": settings.HEARTRATE_QUEUE, "signal": "heart_rate",
             "file": settings.HEARTRATE_CSV_FILE_PATH, "interval": settings.HEARTRATE_INTERVAL},
            # calories
            {"queue": settings.CALORIES_QUEUE, "signal": "calories",
             "file": settings.CALORIES_CSV_FILE_PATH, "interval": settings.CALORIES_INTERVAL},
            # steps
            {"queue": settings.STEPS_QUEUE, "signal": "steps",
             "file": settings.STEPS_CSV_FILE_PATH, "interval": settings.STEPS_INTERVAL},
            # sleep
            {"queue": settings.SLEEP_QUEUE, "signal": "sleep",
             "file": settings.SLEEP_CSV_FILE_PATH, "interval": settings.SLEEP_INTERVAL},
            # intensities
            {"queue": settings.INTENSITIES_QUEUE, "signal": "intensities",
             "file": settings.INTENSITIES_CSV_FILE_PATH, "interval": settings.INTENSITIES_INTERVAL},
        ]

        for cfg in producer_configs:
            producer = BaseProducer(
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