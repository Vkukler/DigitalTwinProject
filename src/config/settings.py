from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent   # root_dir

# producer reading from csv file
HEARTRATE_CSV_FILE_PATH = BASE_DIR / "data" / "user_5577150313_heartrate_seconds_preprocessed.csv"
CALORIES_CSV_FILE_PATH = BASE_DIR / "data" / "user_5577150313_minuteCaloriesNarrow_merged.csv"
STEPS_CSV_FILE_PATH = BASE_DIR / "data" / "user_5577150313_minuteStepsNarrow_merged.csv"
SLEEP_CSV_FILE_PATH = BASE_DIR / "data" / "user_5577150313_minuteSleep_preprocessed.csv"
INTENSITIES_CSV_FILE_PATH = BASE_DIR / "data" / "user_5577150313_minuteIntensitiesNarrow_merged.csv"

# RabbitMq_Setting
RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
RABBITMQ_USER = "admin"
RABBITMQ_PASSWORD = "admin"

#InfluxDB_Setting
INFLUX_HOST = "http://127.0.0.1:8086"
INFLUX_TOKEN = "my-super-secret-token"
INFLUX_DATABASE = "health_db"
INFLUX_ORG = "my-org"


# Exchange
EXCHANGE = "activity_data_exchange"
EXCHANGE_TYPE = "direct"

# Queues for each producer
HEARTRATE_QUEUE = "heartrate_queue"
CALORIES_QUEUE = "calories_queue"
STEPS_QUEUE = "steps_queue"
SLEEP_QUEUE = "sleep_queue"
INTENSITIES_QUEUE = "intensities_queue"

QUEUES = [HEARTRATE_QUEUE, CALORIES_QUEUE, STEPS_QUEUE, SLEEP_QUEUE, INTENSITIES_QUEUE]

# Time Intervals for streaming the data
HEARTRATE_INTERVAL = 1
CALORIES_INTERVAL = 6
STEPS_INTERVAL = 6
SLEEP_INTERVAL = 6
INTENSITIES_INTERVAL = 6

USER_ID = "user_5577150313"

# Flask
FLASK_PORT = 5000

