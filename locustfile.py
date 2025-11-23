import random
from locust import HttpUser, task, between, LoadTestShape

class JuiceShopUser(HttpUser):
    """
    Same realistic user behavior as load test.
    Stress comes from ramping concurrency high.
    """
    wait_time = between(0.5, 2.0)  # slightly faster than load test

    @task(3)
    def homepage(self):
        self.client.get("/", name="GET /")

    @task(5)
    def list_products(self):
        self.client.get("/rest/products", name="GET /rest/products")

    @task(2)
    def search_products(self):
        term = random.choice(["apple", "juice", "lemon", "banana", "shirt", "sticker"])
        self.client.get(f"/rest/products/search?q={term}", name="GET /rest/products/search")

    @task(1)
    def product_details(self):
        product_id = random.randint(1, 20)
        self.client.get(f"/rest/products/{product_id}", name="GET /rest/products/:id")


class StressShape(LoadTestShape):
    """
    Stress profile:
    - 1 min warmup at 10 users
    - then ramp in steps, +25 users every minute
    - stop after 10 minutes or earlier if you kill it manually
    """
    stages = [
        {"duration": 60,  "users": 10,  "spawn_rate": 2},   # warmup
        {"duration": 120, "users": 35,  "spawn_rate": 5},
        {"duration": 180, "users": 60,  "spawn_rate": 8},
        {"duration": 240, "users": 85,  "spawn_rate": 10},
        {"duration": 300, "users": 110, "spawn_rate": 12},
        {"duration": 360, "users": 135, "spawn_rate": 15},
        {"duration": 420, "users": 160, "spawn_rate": 18},
        {"duration": 480, "users": 185, "spawn_rate": 20},
        {"duration": 540, "users": 210, "spawn_rate": 22},
        {"duration": 600, "users": 235, "spawn_rate": 25},  # push hard
    ]

    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
        return None
