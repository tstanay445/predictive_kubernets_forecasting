import math
import random
from locust import HttpUser, task, between, LoadTestShape

class WebsiteUser(HttpUser):
    # Simulates real user "think time" between page loads
    wait_time = between(2, 6)

    @task
    def load_home(self):
        self.client.get("/")

class RealisticDiurnalTraffic(LoadTestShape):
    # Compress a 24-hour cycle into 1 hour (3600 seconds).
    cycle_length = 300  
    base_load = 20       # Minimum traffic at "night"
    peak_amplitude = 100 # Maximum additional users at "midday"

    def tick(self):
        run_time = self.get_run_time()
        
        cycle_position = (run_time % self.cycle_length) / self.cycle_length
        wave_multiplier = (math.sin(cycle_position * 2 * math.pi - (math.pi / 2)) + 1) / 2
        
        target_users = self.base_load + (self.peak_amplitude * wave_multiplier)
        jitter = random.uniform(-0.05, 0.05) * target_users
        
        final_users = int(target_users + jitter)
        spawn_rate = 5 
        return (final_users, spawn_rate)