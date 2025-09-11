from .publisher import RabbitMQPublisher
from .heartbeat_producer import HeartbeatProducer

class ProducerService:
    def __init__(self):
        self.publisher = RabbitMQPublisher()
        self.producers = [
            HeartbeatProducer(self.publisher)
        ]

    def start(self):
        for p in self.producers:
            p.start()
