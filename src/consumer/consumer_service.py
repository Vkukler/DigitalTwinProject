import json
import threading
from consumer.consumer import RabbitMQConsumer

class ConsumerService:
    def __init__(self):
        self.latest_heartbeat = {"heartbeat": 0}
        self.total_steps = 0
        self.lock = threading.Lock()

        # extra storage for analysis
        self.heartbeat_history = []
        self.max_history_size = 50
        self.alerts = []

    def start(self):
        consumer = RabbitMQConsumer(
            self._heartbeat_callback,
            self._activity_callback
        )
        thread = threading.Thread(target=consumer.start, daemon=True)
        thread.start()

    def _heartbeat_callback(self, ch, method, properties, body):
        # parse the message
        data = json.loads(body)

        with self.lock:
            self.latest_heartbeat = data

            # dummy heartbeat analysis process
            # keep history (fixed window size)
            hb = data.get("heartbeat", 0)
            self.heartbeat_history.append(hb)
            if len(self.heartbeat_history) > self.max_history_size:
                self.heartbeat_history.pop(0)

            # simple anomaly detection
            if hb > 120 or hb < 50:
                self.alerts.append(
                    {"msg": f"Abnormal heartbeat detected: {hb}", "timestamp": data.get("timestamp")}
                )

        print(f" [v] Received Heartbeat: {data}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def _activity_callback(self, ch, method, properties, body):
        data = json.loads(body)
        with self.lock:
            self.total_steps += data.get("steps", 0)
        print(f" [v] Received Activity: {data}, Total Steps: {self.total_steps}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
