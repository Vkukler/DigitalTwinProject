import pika
import time
import json
import random

# Modify file path to match the new directory structure
CSV_FILE_PATH = '../docs/data/heartbeat_data.csv'


def produce_data():
    """
    This function reads heartbeat data from a CSV file and sends it to RabbitMQ.
    It also simulates sending activity data periodically.
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declare the queues, making them durable to survive a broker restart
    channel.queue_declare(queue='heartbeat_queue', durable=True)
    channel.queue_declare(queue='activity_queue', durable=True)

    user_id = "user_001"
    heartbeat_count = 0

    try:
        with open(CSV_FILE_PATH, 'r') as file:
            for line in file:
                try:
                    timestamp_str, heartbeat_str = line.strip().split(',')
                    heartbeat_value = int(heartbeat_str)

                    # Create and publish heartbeat message
                    heartbeat_data = {
                        "userId": user_id,
                        "heartbeat": heartbeat_value,
                        "timestamp": timestamp_str
                    }
                    message = json.dumps(heartbeat_data)
                    channel.basic_publish(
                        exchange='',
                        routing_key='heartbeat_queue',
                        body=message,
                        properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
                    )
                    print(f" [x] Sent Heartbeat: {message}")

                    # Simulate sending activity data every 5 heartbeats (or every 25 seconds)
                    heartbeat_count += 1
                    if heartbeat_count % 5 == 0:
                        steps_value = random.randint(100, 500)
                        activity_data = {
                            "userId": user_id,
                            "steps": steps_value,
                            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
                        }
                        message = json.dumps(activity_data)
                        channel.basic_publish(
                            exchange='',
                            routing_key='activity_queue',
                            body=message,
                            properties=pika.BasicProperties(delivery_mode=2)
                        )
                        print(f" [x] Sent Activity: {message}")

                    time.sleep(5)  # Pause for 5 seconds to simulate real-time data flow

                except (ValueError, IndexError):
                    print(f" [!] Skipping invalid line: {line.strip()}")
    except FileNotFoundError:
        print(f" [!] Error: The file {CSV_FILE_PATH} was not found.")
    finally:
        connection.close()
        print(" [√] Production complete. Connection closed.")


if __name__ == "__main__":
    produce_data()
