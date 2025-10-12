import numpy as np
import datetime
from typing import List, Dict, Any, Optional
from collections import deque


class SleepAdvisor:
    """
    Generates daily sleep advice based on:
    - Daily resting heart rate (RHR) during sleep
    - Sleep efficiency metrics
    - 7-day rolling window analysis with robust z-scores
    """

    def __init__(self):
        # For computing daily RHR during sleep
        self.hr_buffer = []
        self.hr_buffer_timestamps = []
        self.is_sleeping = False
        self.last_sleep_state = None
        
        # Store daily RHR values: {date_str: rhr_value}
        self.daily_rhr_history = {}
        
        # For sleep efficiency calculation
        self.sleep_period_start = None 
        self.sleep_minutes = 0  
        self.total_sleep_minutes = 0 
        self.current_date = None
        
        # For advice generation
        self.last_advice_date = None
        self.advice_generated_today = False
        
    def update_heart_rate(self, hr: float, timestamp: str):
        """
        Called every time a heart rate measurement arrives.
        Buffers HR during sleep periods to compute daily RHR.
        """
        dt = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        
        # If currently in sleep state, buffer the heart rate
        if self.is_sleeping:
            self.hr_buffer.append(hr)
            self.hr_buffer_timestamps.append(dt)
    
    def update_sleep(self, sleep_value: int, timestamp: str) -> Optional[Dict[str, Any]]:
        """
        Called every time a sleep measurement arrives (every minute).
        
        Args:
            sleep_value: 0=awake, 1/2/3=asleep (different quality levels)
            timestamp: timestamp string
            
        Returns:
            Advice event dict if it's time to generate advice (8 AM), None otherwise
        """
        dt = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        date_str = dt.strftime("%Y-%m-%d")
        current_hour = dt.hour
        
        # Track if we're in a new day
        if self.current_date != date_str:
            self.current_date = date_str
            self.advice_generated_today = False
        
        # Initialize sleep period tracking (after 18:00)
        if current_hour >= 18 and self.sleep_period_start is None:
            self.sleep_period_start = dt
            self.sleep_minutes = 0
            self.total_sleep_minutes = 0
        
        # Track sleep state transitions
        previous_sleep_state = self.is_sleeping
        self.is_sleeping = (sleep_value in [1, 2, 3])
        
        # Update sleep efficiency counters during sleep period
        if self.sleep_period_start is not None:
            if sleep_value != 0: 
                self.total_sleep_minutes += 1
            if sleep_value == 1: 
                self.sleep_minutes += 1
        
        # Detect transition from sleep to awake
        if previous_sleep_state and not self.is_sleeping:
            # Check if we have enough HR data to compute daily RHR
            if len(self.hr_buffer) >= 60: 
                daily_rhr = np.percentile(self.hr_buffer, 10)
                self.daily_rhr_history[date_str] = daily_rhr
                print(f"[SleepAdvisor] Computed daily RHR for {date_str}: {daily_rhr:.1f} bpm")
            
            # Reset buffer for next sleep period
            self.hr_buffer = []
            self.hr_buffer_timestamps = []
        
        # Check if it's time to generate advice (at or after 8 AM)
        if current_hour >= 8 and not self.advice_generated_today:
            self.advice_generated_today = True
            
            # Calculate sleep efficiency for the night that just passed
            sleep_efficiency = None
            if self.sleep_period_start is not None and self.total_sleep_minutes > 0:
                sleep_efficiency = (self.sleep_minutes / self.total_sleep_minutes) * 100
            
            # Reset sleep period tracking for next night
            self.sleep_period_start = None
            
            # Generate advice
            advice_event = self._generate_advice(date_str, sleep_efficiency, dt)
            return advice_event
        
        return None
    
    def _generate_advice(self, date_str: str, sleep_efficiency: Optional[float], 
                         timestamp: datetime.datetime) -> Dict[str, Any]:
        """
        Generate daily advice using 7-day rolling window analysis.
        """
        # Check if we have enough data (at least 3 days)
        if len(self.daily_rhr_history) < 3:
            return {
                "type": "advice",
                "advice": "Collecting data... Need at least 3 days for personalized advice.",
                "daily_rhr": self.daily_rhr_history.get(date_str, None),
                "previous_rhr": None,
                "delta_rhr": None,
                "sleep_efficiency": sleep_efficiency,
                "recovery_flag": "COLLECTING",
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
        
        # Get sorted dates and RHR values for rolling window
        sorted_dates = sorted(self.daily_rhr_history.keys())
        
        # Get last 7 days of data (or all available if less than 7)
        window_dates = sorted_dates[-7:]
        window_rhrs = [self.daily_rhr_history[d] for d in window_dates]
        
        # Get today's RHR (if available)
        daily_rhr = self.daily_rhr_history.get(date_str, None)
        
        # Get previous day's RHR for delta calculation
        previous_rhr = None
        delta_rhr = None
        if len(sorted_dates) >= 2 and date_str in sorted_dates:
            date_idx = sorted_dates.index(date_str)
            if date_idx > 0:
                previous_rhr = self.daily_rhr_history[sorted_dates[date_idx - 1]]
                if daily_rhr is not None:
                    delta_rhr = daily_rhr - previous_rhr
        
        # Compute robust statistics if we have today's RHR
        if daily_rhr is not None and len(window_rhrs) >= 3:
            # Calculate median over the window
            median = np.median(window_rhrs)
            
            # Calculate MAD (Median Absolute Deviation)
            mad = np.median(np.abs(np.array(window_rhrs) - median))
            
            # Avoid division by zero
            if mad == 0:
                mad = 1.0
            
            # Calculate robust z-score
            z_score = 0.6745 * (daily_rhr - median) / mad
            
            # Determine recovery flag and advice
            if z_score >= 2 or (delta_rhr is not None and delta_rhr >= 5):
                recovery_flag = "RED"
                advice = "Rest day recommended; early bedtime (+60–90 min)."
            elif z_score >= 1.0 or (delta_rhr is not None and delta_rhr >= 3):
                recovery_flag = "AMBER"
                advice = "Go easy today; +45–60 min sleep; avoid late vigorous exercise."
            else:
                recovery_flag = "GREEN"
                advice = "All good; maintain your routine."
            
            return {
                "type": "advice",
                "advice": advice,
                "daily_rhr": round(daily_rhr, 1),
                "previous_rhr": round(previous_rhr, 1) if previous_rhr else None,
                "delta_rhr": round(delta_rhr, 1) if delta_rhr else None,
                "z_score": round(z_score, 2),
                "sleep_efficiency": round(sleep_efficiency, 1) if sleep_efficiency else None,
                "recovery_flag": recovery_flag,
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            # Not enough data for this specific day
            return {
                "type": "advice",
                "advice": "Collecting data for today...",
                "daily_rhr": daily_rhr,
                "previous_rhr": previous_rhr,
                "delta_rhr": delta_rhr,
                "sleep_efficiency": round(sleep_efficiency, 1) if sleep_efficiency else None,
                "recovery_flag": "COLLECTING",
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }

