from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent   # root_dir
CSV_FILE_PATH = BASE_DIR / "data" / "user_5577150313_heartrate_seconds_merged.csv"

RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
RABBITMQ_USER = "admin"
RABBITMQ_PASSWORD = "admin"
# Exchange
EXCHANGE = "activity_data_exchange"
EXCHANGE_TYPE = "direct"
# Queues for each producer
HEARTBEAT_QUEUE = "heartbeat_queue"
ACTIVITY_QUEUE = "activity_queue"

USER_ID = "user_5577150313"


# Flask
FLASK_PORT = 5000

