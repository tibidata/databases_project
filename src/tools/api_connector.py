from typing import Any, Dict, Optional
import logging

import requests


class APIConnector:

    def __init__(self, api_route: str) -> None:
        self.api_route = api_route
        self.user_logged_in = None

    def __call__(
        self,
        process: str,
        values: Optional[Dict[str, Any]] = None,
    ) -> Any:

        if not values:
            values = {}

        return self.post(process=process, values=values)

    def post(self, **kwargs):

        response = requests.post(
            f"{self.api_route}/query",
            json={
                "process": kwargs.get("process"),
                "values": kwargs.get("values"),
            },
            timeout=10,
        )

        if response.status_code == 200:
            logging.debug("Query successful: %s", response.json())
            return response.json()["response"]
        logging.error(
            "Query failed with status %s: %s",
            response.status_code,
            response.text,
        )
        return None

    def check_health(self):
        """
        Checks the health of the backend API.

        Sends a GET request to the root of the API and checks if the service
        is running and reachable.

        Returns:
            bool: True if the health check is successful, False otherwise.
        """
        try:
            response = requests.get(f"{self.api_route}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("\nHealth Check Successful!")
                print("Message:", data.get("message"))
                print("Database:", data.get("database"))
                input("\nPress enter to continue...")
                return True
            print("\nHealth Check Failed. Status Code:", response.status_code)
            print("Response:", response.text)
            return False
        except requests.RequestException as e:
            logging.error("Error connecting to the Backend API: %s", e)
            return False
