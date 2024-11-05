"""
DBClient Module

This module provides a class DBClient that interacts with a backend API
for database operations such as user login, registration, voting, and
election management. It handles HTTP requests to a specified API route
and processes responses for various query types.
"""

import logging

import requests

from tools.query import Query


class DBClient:
    """
    A client class for interacting with a backend API.

    This class is responsible for executing database-related operations
    through a RESTful API. It supports user login, registration,
    election viewing, voting, and election creation.

    Attributes:
        api_route (str): The base URL of the API to which requests will be sent.
        query_type_map (dict): A mapping of query types to corresponding handler methods.
    """

    def __init__(self, api_route: str) -> None:
        """
        Initializes the DBClient with the given API route.

        Args:
            api_route (str): The base URL for the API.
        """
        self.api_route = api_route
        self.query_type_map = {
            "login": self.__validate_login,
            "register": self.__register,
            "view_results": self.__view_elections,
            "list_elections": self.__view_elections,
            "list_live_elections": self.__view_elections,
            "vote": self.__vote,
            "create_election": self.__create_election,
            "list_election_candidates": self.__view_elections,
        }

        self.user_logged_in = None

    def __call__(self, **kwargs):
        """
        Calls the appropriate query handler based on the query_type provided.

        Args:
            **kwargs: The keyword arguments containing query parameters.

        Returns:
            The result of the query handler.

        Raises:
            ValueError: If the query_type is invalid.
        """
        query_type = kwargs.get("query_type")
        handler = self.query_type_map.get(query_type)
        if handler:
            return handler(**kwargs)
        raise ValueError(f"Invalid query_type: {query_type}")

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

    def __validate_login(self, **kwargs) -> bool:
        """
        Validates user login credentials.

        Compares the provided password with the password stored in the database.

        Args:
            **kwargs: Contains 'username' and 'password'.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        result = self.__query(**kwargs)

        if not result["result"]:
            return False

        return result["result"][0]["password"] == kwargs.get("password")

    def __register(self, **kwargs):
        """
        Registers a new user.

        First checks if the user already exists, then attempts to register.

        Args:
            **kwargs: Contains 'username' and 'email'.

        Returns:
            str: A message indicating success or failure.
        """
        if not self.__query(
            query_type="check_user",
            username=kwargs.get("username"),
            email=kwargs.get("email"),
        )["result"]:

            self.__query(**kwargs)

            return True
        return False

    def __view_elections(self, **kwargs):
        """
        Retrieves a list of elections.

        Args:
            **kwargs: Additional parameters for the query.

        Returns:
            list: A list of elections or None if no elections are found.
        """
        results = self.__query(**kwargs).get("result", [])
        return results if results else None

    def __vote(self, **kwargs):
        """
        Records a vote for a candidate in a specific election.

        Checks if the user has already voted in the specified election.

        Args:
            **kwargs: Contains 'username', 'election_name', and 'candidate_name'.

        Returns:
            str: A message indicating success or that the user has already voted.
        """
        if not self.__query(
            query_type="check_vote",
            username=kwargs.get("username"),
            election_name=kwargs.get("election_name"),
        )["result"][0]["has_voted"]:
            self.__query(**kwargs)
            return True
        return False

    def __create_election(self, **kwargs):
        """
        Creates a new election.

        Checks if an election with the same name already exists before creation.

        Args:
            **kwargs: Contains election details and candidates.

        Returns:
            str: A message indicating success or that the election already exists.
        """
        if not self.__query(
            query_type="check_election", election_name=kwargs.get("election_name")
        )["result"][0]["election_exists"]:
            election_id = self.__query(**kwargs)["new_record_id"]

            self.__query(
                query_type="insert_candidates",
                election_id=election_id,
                candidates=kwargs.get("candidates"),
            )

            return True

        return False

    def __query(self, **kwargs):
        """
        Executes a query against the backend API.

        Constructs a SQL query using the Query class and sends it to the API.

        Args:
            **kwargs: Contains parameters to construct the SQL query.

        Returns:
            dict: The response from the API, or None if the query fails.
        """
        sql_query = Query(**kwargs)
        response = requests.post(
            f"{self.api_route}/query", json={"sql_command": sql_query()}, timeout=10
        )
        if response.status_code == 200:
            logging.debug("Query successful: %s", response.json())
            return response.json()
        logging.error(
            "Query failed with status %s: %s", response.status_code, response.text
        )
        return None
