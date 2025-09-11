import pika
from config import settings

class RabbitMQConsumer:
    def __init__(self, on_heartbeat, on_activity):

        credentials = pika.PlainCredentials(
            username=settings.RABBITMQ_USER,
            password=settings.RABBITMQ_PASSWORD
        )

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(settings.RABBITMQ_HOST,
                                      port=settings.RABBITMQ_PORT,
                                      credentials = credentials
                                      )
        )
        self.channel = self.connection.channel()

        # declare exchange
        self.channel.exchange_declare(exchange=settings.EXCHANGE, exchange_type=settings.EXCHANGE_TYPE)

        # declare queue
        self.channel.queue_declare(queue=settings.HEARTBEAT_QUEUE, durable=True)
        self.channel.queue_declare(queue=settings.ACTIVITY_QUEUE, durable=True)

        # binding queue to the exchange
        self.channel.queue_bind( exchange=settings.EXCHANGE, queue=settings.HEARTBEAT_QUEUE, routing_key=settings.HEARTBEAT_QUEUE)
        self.channel.queue_bind(exchange=settings.EXCHANGE, queue=settings.ACTIVITY_QUEUE, routing_key=settings.ACTIVITY_QUEUE)

        # callback setting
        self.channel.basic_consume(
            queue=settings.HEARTBEAT_QUEUE,
            on_message_callback=on_heartbeat,
            auto_ack=False
        )
        self.channel.basic_consume(
            queue=settings.ACTIVITY_QUEUE,
            on_message_callback=on_activity,
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
