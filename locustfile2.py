import random
from locust import HttpUser, task, between

class JuiceShopUser(HttpUser):
    """
    Realistic anonymous user behavior for a load test.
    """
    wait_time = between(1, 3)  # think time like a real user

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
        # Pick an ID that likely exists; Juice Shop usually has many products.
        product_id = random.randint(1, 20)
        self.client.get(f"/rest/products/{product_id}", name="GET /rest/products/:id")
