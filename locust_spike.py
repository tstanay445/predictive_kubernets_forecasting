
from locust import HttpUser, task, between, LoadTestShape


class WebsiteUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def load_home(self):
        self.client.get("/")


class SuddenSpikeShape(LoadTestShape):
    """
    Ten-minute workload with irregular sudden traffic spikes.
    """

    stages = [
        (120, 20),
        (180, 100),
        (300, 20),
        (360, 140),
        (480, 20),
        (540, 80),
        (600, 20),
    ]

    def tick(self):
        run_time = self.get_run_time()

        for end_time, users in self.stages:
            if run_time < end_time:
                print(
                    f"Runtime: {run_time:.1f}s | "
                    f"Target users: {users}"
                )
                return users, 10

        print("10-minute workload completed.")
        return None

