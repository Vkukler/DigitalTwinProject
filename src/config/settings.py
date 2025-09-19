from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent   # root_dir

# producer reading from csv file
HEARTRATE_CSV_FILE_PATH = BASE_DIR / "data" / "user_5577150313_heartrate_seconds_preprocessed.csv"
CALORIES_CSV_FILE_PATH = BASE_DIR / "data" / "user_5577150313_minuteCaloriesNarrow_merged.csv"
STEPS_CSV_FILE_PATH = BASE_DIR / "data" / "user_5577150313_minuteStepsNarrow_merged.csv"
SLEEP_CSV_FILE_PATH = BASE_DIR / "data" / "user_5577150313_minuteIntensitiesNarrow_merged.csv"
INTENSITIES_FILE_PATH = BASE_DIR / "data" / "user_5577150313_minuteSleep_merged.csv"

# RabbitMq_Setting
RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
RABBITMQ_USER = "admin"
RABBITMQ_PASSWORD = "admin"

# Exchange
EXCHANGE = "activity_data_exchange"
EXCHANGE_TYPE = "direct"

# Queues for each producer
HEARTRATE_QUEUE = "heartrate_queue"
ACTIVITY_QUEUE = "activity_queue"
CALORIES_QUEUE = "calories_queue"

# Time Intervals for streaming the data
HEARTRATE_INTERVAL = 1
ACTIVITY_INTERVAL = 6
CALORIES_INTERVAL = 6

USER_ID = "user_5577150313"

# Flask
FLASK_PORT = 5000

