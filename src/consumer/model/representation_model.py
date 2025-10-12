import json
import datetime
from .algorithm.classifier import SimpleClassifier
from .algorithm.sleep_advisor import SleepAdvisor

class RepresentationModel:
    def __init__(self, person: str):
        """
        Initialize the representation model for a specific person.
        Args:
            person (str): Unique identifier of the individual being modeled.
        """
        self.person = person
        self.timestamp = None
        self.classifier = SimpleClassifier()
        self.sleep_advisor = SleepAdvisor()
        self.signals = {
            "calories": 0.0,
            "steps": 0.0,
            "sleep": 0,
            "heart_rate": 0.0,
            "heart_rate_status": 0,
            "intensities": 0
        }
        self.detected_events = []
        self.advice_events = []

    def update(self, raw_event: dict):
        '''
        Update the model's internal state based on a list of incoming events.

        Each event represents a new observation or an AI-derived insight.
        The method applies transition rules to modify signal values and
        maintains the latest known timestamp.

        :param events: A list of event objects containing keys such as
                "type", "signal", "value", and "timestamp".
        '''

        # clear previous detected events
        self.detected_events = []
        self.advice_events = []

        for event in self._process_event(raw_event):
            event_ts = datetime.datetime.strptime(event.get("timestamp"), "%Y-%m-%d %H:%M:%S")

            # keep the latest timestamp
            if self.timestamp is None or event_ts >= self.timestamp:
                self.timestamp = event_ts


            if event["type"] == "measurement":
                self.signals[event["signal"]] = event["value"]

            elif event["type"] == "anomaly":
                self.detected_events.append(event)
            
            elif event["type"] == "advice":
                self.advice_events.append(event)

    def _process_event(self, raw_event):
        """
            Process an incoming raw event and perform additional logic if required.
            Args:
                raw_event (dict): The incoming event parsed from JSON.
            Returns:
                list: A list containing the original event and any derived events.
        """
        events = [raw_event]

        # Process heart rate measurements
        if raw_event["type"] == "measurement" and raw_event["signal"] == "heart_rate":
            hr = raw_event["value"]
            timestamp = raw_event["timestamp"]
            
            # Update classifier for anomaly detection
            anomaly_events = self.classifier.update(hr=hr, timestamp=timestamp)

            # Convert classifier output into standard event dicts
            for a in anomaly_events:
                derived_event = {
                    "type": "anomaly",
                    "anomaly_type": a["type"],
                    "score": a.get("score", None),
                    "message": a["message"],
                    "timestamp": a["timestamp"],
                }
                events.append(derived_event)
            
            # Update sleep advisor with heart rate
            self.sleep_advisor.update_heart_rate(hr=hr, timestamp=timestamp)
        
        # Process sleep measurements
        if raw_event["type"] == "measurement" and raw_event["signal"] == "sleep":
            sleep_value = int(raw_event["value"])
            timestamp = raw_event["timestamp"]
            
            # Update sleep advisor
            advice_event = self.sleep_advisor.update_sleep(
                sleep_value=sleep_value, 
                timestamp=timestamp
            )
            
            # If advice was generated, add it to events
            if advice_event is not None:
                events.append(advice_event)
        
        return events

    def to_dict(self):
        '''
        Convert the current model state into a dictionary representation.
        '''
        return {
            "timestamp": self.timestamp,
            "person": self.person,
            "signals": self.signals,
            "anomaly_events": self.detected_events[-10:],  # last few anomalies
            "advice_events": self.advice_events,
        }