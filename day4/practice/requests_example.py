import requests

def get_users() -> None:
    url = "https://jsonplaceholder.typicode.com/users"

    try:
        response = requests.get(url, timeout=10)

        response.raise_for_status()

        users = response.json()

        print(f"HTTP Status: {response.status_code}")
        print(f"Total users: {len(users)}")

        print("\nUser Details:")

        for user in users:
            print(
                f"ID: {user['id']} | "
                f"Name: {user['name']} | "
                f"Email: {user['email']}"
            )

    except requests.RequestException as error:
        print(f"API request failed: {error}")
if __name__ == "__main__":
    get_users()

#Run requests_example.py and check that the program displays the users returned by the API.

import requests


def get_users() -> None:
    url = "https://jsonplaceholder.typicode.com/users"

    try:
        # Send GET request to API
        response = requests.get(url, timeout=10)

        # Check for HTTP errors
        response.raise_for_status()

        # Convert JSON response to Python data
        users = response.json()

        print(f"HTTP Status: {response.status_code}")
        print(f"Total Users: {len(users)}")

        print("\nUser Details:")
        print("-" * 50)

        for user in users:
            print(f"ID: {user['id']}")
            print(f"Name: {user['name']}")
            print(f"Email: {user['email']}")
            print(f"City: {user['address']['city']}")
            print("-" * 50)

    except requests.Timeout:
        print("Error: API request timed out.")

    except requests.ConnectionError:
        print("Error: Unable to connect to the API.")

    except requests.HTTPError as error:
        print(f"HTTP Error: {error}")

    except requests.RequestException as error:
        print(f"Request failed: {error}")
if __name__ == "__main__":
    get_users()
