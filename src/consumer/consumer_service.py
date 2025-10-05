import json
import threading
from consumer.consumer import RabbitMQConsumer
from consumer.model.representation_model import RepresentationModel
from consumer.ai.ai_implementation import heart_rate_anomaly_detection


class ConsumerService:
    """
        Service that listens for incoming events from RabbitMQ, processes them,
        and updates the internal user representation model accordingly.
    """

    def __init__(self, person="user_5577150313"):
        self.model = RepresentationModel(person)
        self.lock = threading.Lock()

    def start(self):
        """
            Start the RabbitMQ consumer in a background thread.
            This allows the main thread to continue running without blocking.
        """
        consumer = RabbitMQConsumer(self._on_message)
        thread = threading.Thread(target=consumer.start, daemon=True)
        thread.start()

    def _on_message(self, ch, method, properties, body):
        """
            Callback function triggered whenever a new message arrives from RabbitMQ.
            Args:
                body (bytes): The raw message body in JSON format.
            Returns:
                list: the current state of user
        """
        raw_event = json.loads(body)
        events_to_apply = self._process_event(raw_event)

        with self.lock:
            self.model.update(events_to_apply)

        print(f" [v] Updated state: {self.model.to_dict()}")
        return self.model.to_dict()

    def _process_event(self, raw_event):
        """
            Process an incoming raw event and perform additional logic if required.
            Args:
                raw_event (dict): The incoming event parsed from JSON.
            Returns:
                list: A list containing the original event and any derived events.
        """
        events = [raw_event]

        # If the event is a measurement(from rabbitMq)
        if raw_event["type"] == "measurement":
            if raw_event["signal"] == "heart_rate":
                derived_event = heart_rate_anomaly_detection(raw_event)
                events.append(derived_event)
        return events