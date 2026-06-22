import numpy as np
import datetime
from typing import List, Dict, Any


class SlidingWindow:
    """A simple sliding window buffer for recent heart_rate values."""

    def __init__(self, window_size: int):
        self.window_size = window_size
        self.values: List[float] = []
        self.timestamps: List[datetime.datetime] = []

    def add(self, value: float, timestamp: datetime.datetime):
        self.values.append(value)
        self.timestamps.append(timestamp)
        # keep window length
        if len(self.values) > self.window_size:
            self.values.pop(0)
            self.timestamps.pop(0)

    def get_values(self):
        return np.array(self.values)

    def duration(self):
        if len(self.timestamps) < 2:
            return 0
        return (self.timestamps[-1] - self.timestamps[0]).total_seconds()


class SimpleClassifier:
    """
    Detects heart rate anomalies using:
    - Sliding Window Robust Variability Detection (MAD-based)
    - Rate-of-Change (spike/drop) detection
    - Tachycardia/Bradycardia thresholds with persistence
    """

    def __init__(self):
        # sliding window for last 5 minutes (assume 10 seconds/sampling → 30 samples)
        self.hr_window = SlidingWindow(window_size=30)
        self.alert_persistence = 6  # 6*10 seconds required for sustained abnormality
        self.last_alert_time = None
        self.consecutive_abnormal_count = 0

    def detect_variability(self) -> Dict[str, Any]:
        """Detect abnormal variability using robust z-score (MAD-based)."""
        values = self.hr_window.get_values()
        if len(values) < 10:
            return None

        median = np.median(values)
        mad = np.median(np.abs(values - median))
        if mad == 0:
            return None

        z_scores = 0.6745 * (values - median) / mad
        last_z = z_scores[-1]

        if abs(last_z) > 3:
            return {
                "type": "variability_anomaly",
                "score": round(float(last_z), 2),
                "message": f"Heart rate deviates from baseline (z={last_z:.2f})"
            }
        return None

    def detect_spike_or_drop(self) -> Dict[str, Any]:
        """Detect sudden heart rate spikes or drops."""
        values = self.hr_window.get_values()
        if len(values) < 30:
            return None

        # compare short-term (50s) vs medium-term (600s) averages
        short_avg = np.mean(values[-5:])
        medium_avg = np.mean(values)
        diff = short_avg - medium_avg

        if diff > 15:
            return {"type": "spike", "score": diff, "message": "Sudden HR spike detected"}
        elif diff < -15:
            return {"type": "drop", "score": diff, "message": "Sudden HR drop detected"}
        return None

    def detect_thresholds(self, hr: float, dt: datetime.datetime) -> Dict[str, Any]:
        """Detect tachycardia/bradycardia with persistence logic."""
        threshold_event = None
        if hr > 110:
            self.consecutive_abnormal_count += 1
            threshold_event = "tachycardia"
        elif hr < 50:
            self.consecutive_abnormal_count += 1
            threshold_event = "bradycardia"
        else:
            self.consecutive_abnormal_count = 0

        # if abnormal persists long enough
        if self.consecutive_abnormal_count >= self.alert_persistence:
            self.consecutive_abnormal_count = 0
            return {
                "type": threshold_event,
                "score": hr,
                "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "message": f"Persistent {threshold_event} detected ({hr:.1f} bpm)"
            }
        return None

    def update(self, hr: float, timestamp: str) -> List[Dict[str, Any]]:
        """Main entry: update classifier with a new heart rate sample."""
        dt = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        self.hr_window.add(hr, dt)

        events = []
        for detector in [self.detect_variability, self.detect_spike_or_drop]:
            result = detector()
            if result:
                result["timestamp"] = dt.strftime("%Y-%m-%d %H:%M:%S")
                events.append(result)

        threshold_result = self.detect_thresholds(hr, dt)
        if threshold_result:
            events.append(threshold_result)

        return events
