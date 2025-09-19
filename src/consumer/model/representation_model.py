import json


class RepresentationModel:
    def __init__(self, person: str):
        self.person = person
        self.timestamp = None
        self.signals = {
            "calories": 0,
            "steps": 0,
            "sleep": 0,
            "heart_rate": 0,
            "heart_rate_status": "",
            "intensities": 0
        }


    def update(self, events: list[dict]):
        """Apply transition rules based on a list of events"""
        if len(events)==2:
            print(events[1])
        for event in events:
            self.timestamp = event.get("timestamp")

            if event["type"] == "measurement":
                self.signals[event["signal"]] = event["value"]

            elif event["type"] == "ai":
                self.signals[f"{event['signal']}_status"] = event["value"]


    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "person": self.person,
            "signals": self.signals
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, person: str, data: str):
        """Reconstruct a model from serialized JSON"""
        obj = cls(person)
        state = json.loads(data)
        obj.timestamp = state.get("timestamp")
        obj.signals = state.get("signals", {})
        return obj
