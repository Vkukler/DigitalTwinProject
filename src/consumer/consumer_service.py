import json
import threading
from consumer.consumer import RabbitMQConsumer
from consumer.model.representation_model import RepresentationModel
from consumer.ai.ai_implementation import heart_rate_anomaly_detection


class ConsumerService:
    def __init__(self, person="user_5577150313"):
        # self.model = RepresentationModel(person)
        self.lock = threading.Lock()

    def start(self):
        consumer = RabbitMQConsumer(self._on_message)
        thread = threading.Thread(target=consumer.start, daemon=True)
        thread.start()

    def _on_message(self, ch, method, properties, body):
        raw_event = json.loads(body)
        events_to_apply = self._process_event(raw_event)

        # with self.lock:
        #     self.model.update(events_to_apply)

        # print(f" [v] Updated state: {self.model.to_dict()}")
        return events_to_apply

    def _process_event(self, raw_event):
        # Start with the incoming raw event
        events = [raw_event]

        # If the event is a measurement(from rabbitMq), check if extra processing is needed
        if raw_event["type"] == "measurement":
            if raw_event["signal"] == "heart_rate":
                derived_event = heart_rate_anomaly_detection(raw_event)
                events.append(derived_event)

        return events