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
                points = []
                # apply state transition logic with on_message func
                representation_model_dict = self.on_message(ch, method, properties, body)

                signal = representation_model_dict["signals"]

                # write the user state
                point = (
                    Point("user_health")
                    .tag("user_id", "user_5577150313")
                    .field("heart_rate", float(signal["heart_rate"]))
                    .field("calories", float(signal["calories"] ))
                    .field("steps", float(signal["steps"]))
                    .field("sleep", int(signal["sleep"]))
                    .field("heart_rate_status", int(signal["heart_rate_status"]))
                    .field("intensities", int(signal["intensities"]))
                    .time(representation_model_dict["timestamp"])
                )
                points.append(point)

                # add some anomaly events
                anomaly_events = representation_model_dict["anomaly_events"]
                if len(anomaly_events)!= 0:
                    for event in anomaly_events:
                        points.append(Point("anomalies")
                                                .tag("user_id", "user_5577150313")
                                                .tag("anomaly_type", event["anomaly_type"]) # "drops", "rise", ""
                                                .field("message", event["message"])
                                                .field("score", event["score"])
                                                .time(event["timestamp"])
                                            )
                
                # add advice events
                advice_events = representation_model_dict.get("advice_events", [])
                if len(advice_events) != 0:
                    for event in advice_events:
                        advice_point = (
                            Point("advice")
                            .tag("user_id", "user_5577150313")
                            .tag("recovery_flag", event.get("recovery_flag", "UNKNOWN"))
                            .field("advice", event["advice"])
                            .field("sleep_efficiency", event.get("sleep_efficiency", 0.0) or 0.0)
                            .time(event["timestamp"].dt.date)
                        )
                        
                        # Only add delta_rhr to InfluxDB
                        if event.get("delta_rhr") is not None:
                            advice_point = advice_point.field("delta_rhr", float(event["delta_rhr"]))
                        points.append(advice_point)
                
                # write this to influxDB
                try:
                    client.write(points)
                    if len(advice_events) != 0:
                        print(f"Written to influxDB: {representation_model_dict}")

                except InfluxDBError as e:
                    print(f"Error writing to InfluxDB: {e}")


                # data persistence with influxDB
                # for event in events:
                #
                #     signal = str(event["signal"])
                #     value = event["value"]
                #
                #     point = (
                #         Point("health_statics")
                #         .tag("user_id", "user_5577150313")
                #         .tag("type", str(event["type"]))
                #         .tag("signal", signal)
                #         .field("past_time", event["timestamp"])
                #         .time(event["timestamp"])
                #     )
                #
                #     # set correct field type
                #     if signal in ["heart_rate", "calories", "steps"]:
                #         point = point.field("value", float(value))
                #     elif signal in ["sleep", "heart_rate_status", "intensities"]:
                #         point = point.field("int_value", int(value))

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
