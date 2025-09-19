import pika
from config import settings


class RabbitMQConsumer:
    def __init__(self, on_message):
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

        # callback setting
        for queue in settings.QUEUES:
            self.channel.basic_consume(
                queue=queue,
                on_message_callback=on_message,
                auto_ack=False
            )

    def start(self):
        print(" [!] Waiting for messages. To exit press CTRL+C")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
        finally:
            self.connection.close()
