import datetime

import pika
import json
from config import settings
from influxdb_client_3 import InfluxDBClient3, InfluxDBError, Point


influxdb_host = settings.INFLUX_HOST
influxdb_token = settings.INFLUX_TOKEN
influxdb_database = settings.INFLUX_DATABASE

client = InfluxDBClient3(
    host=influxdb_host,
    token=influxdb_token,
    database=influxdb_database,
    org = settings.INFLUX_ORG,
)


class RabbitMQConsumer:
    def __init__(self, on_message):
        self.on_message = on_message

        credentials = pika.PlainCredentials(
            username=settings.RABBITMQ_USER,
            password=settings.RABBITMQ_PASSWORD
        )

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                credentials=credentials
            )
        )
        self.channel = self.connection.channel()

        # declare exchange
        self.channel.exchange_declare(exchange=settings.EXCHANGE,
                                      exchange_type=settings.EXCHANGE_TYPE)

        # declare & bind queues
        for queue in settings.QUEUES:
            self.channel.queue_declare(queue=queue, durable=True)
            self.channel.queue_bind(exchange=settings.EXCHANGE,
                                    queue=queue,
                                    routing_key=queue)
            

        def make_callback(queue_name):
            def callback(ch, method, properties, body):

                # apply state transition logic with on_message func
                model_state = self.on_message(ch, method, properties, body)

                # data persistence with influxDB
                point = (
                    Point("health_statics")
                    .tag("user_id", str(model_state["person"]))
                    .field("calories", float(model_state["signals"]["calories"]))
                    .field("steps", int(model_state["signals"]["steps"]))
                    .field("sleep", int(model_state["signals"]["sleep"]))
                    .field("heart_rate", float(model_state["signals"]["heart_rate"]))
                    .field("heart_rate_status", str(model_state["signals"]["heart_rate_status"]))
                    .field("intensities", int(model_state["signals"]["intensities"]))
                    .field("past_time", str(model_state["timestamp"]))
                    .time(datetime.datetime.utcnow())
                )
                try:
                    client.write(point)
                    print(f"Written to {queue_name}: {model_state}")

                except InfluxDBError as e:
                    print(f"Error writing to InfluxDB: {e}")
            return callback
        
        for queue in settings.QUEUES:
            self.channel.basic_consume(
                queue=queue,
                on_message_callback=make_callback(queue),
                auto_ack= True
            )

    def start(self):
        print(" [!] Waiting for messages. To exit press CTRL+C")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
        finally:
            self.connection.close()
