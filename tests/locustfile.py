from locust import HttpUser, task, between


class CustomerAPITestUser(HttpUser):
    wait_time = between(1, 5)  # Set request timeout interval from 1 to 5 seconds

    @task
    def get_customers(self):
        # Send request to /customers
        response = self.client.get("/api/v1/customers")
        if response.status_code == 200:
            print(f"Successfully retrieved customers: {len(response.json())} entries")
        else:
            print(f"Failed to retrieve customers. Status code: {response.status_code}")


"""To-DO: New TestCases"""
