"""
DBClient Module

This module provides a class DBClient that interacts with a backend API
for database operations such as user login, registration, voting, and
election management. It handles HTTP requests to a specified API route
and processes responses for various query types.
"""

import os
import logging

from tools.query import Query
import mysql.connector


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

    def __init__(self) -> None:
        """
        Initializes the DBClient with the given API route.

        Args:
            api_route (str): The base URL for the API.
        """
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

        self.db_config = {
            "host": os.getenv("MYSQL_HOST", "db"),
            "user": os.getenv("MYSQL_USER", "user"),
            "password": os.getenv("MYSQL_PASSWORD", "password"),
            "database": os.getenv("MYSQL_DATABASE", "testdb"),
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
            # Establish database connection
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            database_name = cursor.fetchone()
            cursor.close()
            connection.close()
            return {
                "message": "Connected to MySQL!",
                "database": database_name,
            }

        except mysql.connector.Error as err:
            # Return an error message in case of database connection failure
            return {
                "error": str(err),
            }

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

        logging.info(result)

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
        query = Query(**kwargs)

        sql_query = query()

        logging.info(sql_query)

        try:
            # Establish database connection
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()

            # Execute the SQL command
            cursor.execute(sql_query)

            # If the command is an INSERT, commit changes and retrieve the new record ID
            if sql_query.strip().lower().startswith("insert"):
                connection.commit()
                new_id = cursor.lastrowid
                response = {
                    "response": "Record inserted successfully!",
                    "command": sql_query,
                    "new_record_id": new_id,
                }

            # For UPDATE or DELETE commands, commit changes and acknowledge success
            elif sql_query.strip().lower().startswith(("update", "delete")):
                connection.commit()
                response = {
                    "response": "Command executed successfully!",
                    "command": sql_query,
                }

            # For SELECT commands, fetch results and include them in the response
            else:
                result = cursor.fetchall()
                columns = (
                    [desc[0] for desc in cursor.description]
                    if cursor.description
                    else []
                )
                response = {
                    "response": "Query executed successfully!",
                    "command": sql_query,
                    "result": [dict(zip(columns, row)) for row in result],
                }

            cursor.close()
            connection.close()
            logging.info("response")
            return response

        except mysql.connector.Error as err:
            # Return an error message if any MySQL error occurs during execution
            return {"error": str(err)}, 500
