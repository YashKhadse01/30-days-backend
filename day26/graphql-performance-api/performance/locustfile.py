
from locust import HttpUser, between, task


GRAPHQL_QUERY = """
query {
    tasks {
        id
        title
        completed
        project {
            id
            name
        }
    }
}
"""


class GraphQLUser(HttpUser):
    wait_time = between(1, 2)

    @task(4)
    def graphql_tasks(self):
        with self.client.post(
            "/graphql",
            json={"query": GRAPHQL_QUERY},
            name="GraphQL - Nested Tasks",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"HTTP {response.status_code}"
                )
                return

            try:
                body = response.json()
            except ValueError:
                response.failure("Invalid JSON response")
                return

            if body.get("errors"):
                response.failure(
                    f"GraphQL errors: {body['errors']}"
                )
            elif not isinstance(
                body.get("data", {}).get("tasks"), list
            ):
                response.failure("Missing tasks data")
            else:
                response.success()

    @task(1)
    def health_check(self):
        self.client.get(
            "/health",
            name="Health Check",
        )
