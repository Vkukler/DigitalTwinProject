import pika
import json
from config import settings

class RabbitMQPublisher:
    def __init__(self):
        credentials = pika.PlainCredentials(
            username=settings.RABBITMQ_USER,
            password=settings.RABBITMQ_PASSWORD
        )

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(settings.RABBITMQ_HOST,
                                      port = settings.RABBITMQ_PORT,
                                      credentials = credentials
                                      )
        )
        self.channel = self.connection.channel()

        # declare the exchange and queues
        self.channel.exchange_declare(exchange=settings.EXCHANGE, exchange_type= settings.EXCHANGE_TYPE)
        self.channel.queue_declare(queue=settings.HEARTRATE_QUEUE, durable=True)
        self.channel.queue_declare(queue=settings.CALORIES_QUEUE, durable=True)

        # bind the queue to exchange
        self.channel.queue_bind(exchange=settings.EXCHANGE, queue=settings.HEARTRATE_QUEUE, routing_key=settings.HEARTRATE_QUEUE)
        self.channel.queue_bind(exchange=settings.EXCHANGE, queue=settings.CALORIES_QUEUE, routing_key=settings.CALORIES_QUEUE)

    def publish(self, queue_name: str, message: dict):
        """publish message to specified queue"""
        self.channel.basic_publish(
            exchange= settings.EXCHANGE,
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),  # message persistence
        )
        print(f" [x] Sent to {queue_name}: {message}")

    def close(self):
        self.connection.close()
