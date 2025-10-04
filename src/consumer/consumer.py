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
                events = self.on_message(ch, method, properties, body)

                # data persistence with influxDB
                for event in events:

                    signal = str(event["signal"])
                    value = event["value"]

                    point = (
                        Point("health_statics")
                        .tag("user_id", "user_5577150313")
                        .tag("type", str(event["type"]))
                        .tag("signal", signal)
                        .field("past_time", event["timestamp"])
                        .time(event["timestamp"])
                    )

                    # set correct field type
                    if signal in ["heart_rate", "calories", "steps"]:
                        point = point.field("value", float(value))
                    elif signal in ["sleep", "heart_rate_status", "intensities"]:
                        point = point.field("int_value", int(value))
                    try:
                        client.write(point)
                        print(f"Written to influxDB: {event}")

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
