import json
import datetime

class RepresentationModel:
    def __init__(self, person: str):
        """
        Initialize the representation model for a specific person.
        Args:
            person (str): Unique identifier of the individual being modeled.
        """
        self.person = person
        self.timestamp = None
        self.signals = {
            "calories": 0.0,
            "steps": 0.0,
            "sleep": 0,
            "heart_rate": 0.0,
            "heart_rate_status": 0,
            "intensities": 0
        }

    def update(self, events: list[dict]):
        '''
        Update the model's internal state based on a list of incoming events.

        Each event represents a new observation or an AI-derived insight.
        The method applies transition rules to modify signal values and
        maintains the latest known timestamp.

        :param events: A list of event objects containing keys such as
                "type", "signal", "value", and "timestamp".
        '''

        for event in events:
            event_ts = datetime.datetime.strptime(event.get("timestamp"), "%Y-%m-%d %H:%M:%S")

            # keep the latest timestamp
            if self.timestamp is None or event_ts >= self.timestamp:
                self.timestamp = event_ts


            if event["type"] == "measurement":
                self.signals[event["signal"]] = event["value"]

            elif event["type"] == "ai":
                self.signals["heart_rate_status"] = event["value"]


    def to_dict(self):
        '''
        Convert the current model state into a dictionary representation.
        '''
        return {
            "timestamp": self.timestamp,
            "person": self.person,
            "signals": self.signals
        }

    # def to_json(self):
    #     return json.dumps(self.to_dict())

    # @classmethod
    # def from_json(cls, person: str, data: str):
    #     """Reconstruct a model from serialized JSON"""
    #     obj = cls(person)
    #     state = json.loads(data)
    #     obj.timestamp = state.get("timestamp")
    #     obj.signals = state.get("signals", {})
    #     return obj
