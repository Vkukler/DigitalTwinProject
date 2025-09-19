class DerivedEvent:
    def __init__(self, timestamp, type, signal, value):
        self.timestamp = timestamp
        self.type = type
        self.signal = signal
        self.value = value

    def to_dict(self):
        return {"timestamp": self.timestamp,
                "type": self.type,
                "signal": self.signal,
                "value": self.value}

