import pika
import json
import os
from config import settings

class RabbitMQPublisher:
    """
    Handles low-level RabbitMQ setup:
    - Declares exchanges and queues
    - Binds queues
    - Manages connections and publishing
    """
    def __init__(self, queue_name:str):

        self.queue_name = queue_name

        credentials = pika.PlainCredentials(
            username=settings.RABBITMQ_USER,
            password=settings.RABBITMQ_PASSWORD
        )

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="rabbitmq", #settings.RABBITMQ_HOST
                                      port=settings.RABBITMQ_PORT,
                                      credentials=credentials
                                      )
        )
        self.channel = self.connection.channel()

        # declare the exchange and queues
        self.channel.exchange_declare(exchange=settings.EXCHANGE, exchange_type= settings.EXCHANGE_TYPE)
        self.channel.queue_declare(queue = self.queue_name, durable=True)

        # bind the queue to exchange
        self.channel.queue_bind(exchange=settings.EXCHANGE, queue= queue_name,
                                    routing_key = self.queue_name)


    def publish(self, message: dict):
        """publish message to specified queue"""
        self.channel.basic_publish(
            exchange= settings.EXCHANGE,
            routing_key= self.queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),  # message persistence
        )
        print(f" [x] Sent to {self.queue_name}: {message}")

    def close(self):
        self.connection.close()
