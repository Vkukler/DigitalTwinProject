from consumer.ai.derived_event import DerivedEvent

def heart_rate_anomaly_detection(event):
    """
    Perform anomaly detection on heart rate measurement.
    Returns a derived AI event if anomaly is detected, otherwise None.
    """
    if event["type"] == "measurement" and event["signal"] == "heart_rate":
        if event["value"] > 120:  # simple threshold rule
            return DerivedEvent(
                timestamp=event["timestamp"],
                type = "ai",
                signal = "heart_rate_status",
                value = "abnormal",
            ).to_dict();
    return event
