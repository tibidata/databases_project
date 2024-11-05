"""
Module: query_builder

This module defines the Query class, which generates SQL queries dynamically based on
specific query types. The class supports a range of election-related queries including 
user login, registration, vote counting, and election creation with candidates. 
Each query type is mapped to its corresponding method, and the class dynamically builds 
the correct query based on the provided query type and parameters.

Classes:
    Query - Builds SQL queries based on given parameters and query type.
"""

import datetime


class Query:
    """
    A class to dynamically build SQL queries based on the provided query type and arguments.

    Attributes:
        args (dict): A dictionary of arguments required to build the specific SQL query.

    Methods:
        __call__(): Returns the generated SQL query.
        __generate_query(): Maps the query type to the corresponding method to build the SQL.
        __login_query(): Generates a SQL query for user login verification.
        __register_query(): Generates a SQL query to register a new user.
        __check_user_query(): Generates a SQL query to check if a user exists by username or email.
        __view_results_query(): Generates a SQL query to view election results.
        __list_elections_query(): Generates a SQL query to list all elections.
        __check_vote_query(): Generates a SQL query to check if a
        user has voted in a specific election.
        __vote_query(): Generates a SQL query to register a user's vote.
        __check_election_query(): Generates a SQL query to check if an election exists.
        __create_election: Generates SQL query to create a new election.
        __insert_candidates: Generates SQL query to insert the new candidates.
    """

    def __init__(self, **kwargs) -> None:
        """
        Initializes the Query class with arguments required to generate the query.

        Args:
            **kwargs: Arbitrary keyword arguments containing details for building the SQL query.
        """
        self.args = kwargs

    def __call__(self):
        """
        Makes the instance callable and triggers the SQL query generation process.

        Returns:
            str: The generated SQL query string.
        """
        return self.__generate_query()

    def __generate_query(self):
        """
        Maps the query type to the corresponding method to generate the SQL query.

        Returns:
            str: The generated SQL query.

        Raises:
            ValueError: If an invalid query type is specified.
        """
        query_map = {
            "login": self.__login_query,
            "register": self.__register_query,
            "check_user": self.__check_user_query,
            "view_results": self.__view_results_query,
            "list_elections": self.__list_elections_query,
            "check_vote": self.__check_vote_query,
            "vote": self.__vote_query,
            "check_election": self.__check_election_query,
            "create_election": self.__create_election,
            "insert_candidates": self.__insert_candidates,
            "list_live_elections": self.__list_live_elections_query,
            "list_election_candidates": self.__list_election_candidates_query,
        }

        # Retrieve the method associated with the specified query type
        query_type = self.args["query_type"]
        if query_type in query_map:
            return query_map[query_type]()
        else:
            raise ValueError("Invalid query type specified")

    def __list_election_candidates_query(self):

        return f"""
            SELECT c.id, c.name, c.birth_date, c.occupation, c.program
            FROM Candidates AS c
            JOIN Elections AS e ON c.election_id = e.id
            WHERE e.name = '{self.args["election_name"]}';
            """

    def __list_live_elections_query(self):

        return f"""
        SELECT * FROM Elections 
        WHERE start_time <= '{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}' 
        AND end_time >= '{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}';
        """

    # Individual query methods for each query type
    def __login_query(self):
        """
        Generates a SQL query for user login.

        Returns:
            str: SQL query to retrieve the password for the specified username.
        """
        return f"SELECT password FROM Users WHERE username='{self.args['username']}';"

    def __register_query(self):
        """
        Generates a SQL query for user registration.

        Returns:
            str: SQL query to insert a new user record.
        """
        return (
            "INSERT INTO Users (username, email, password, last_login) "
            f"VALUES ('{self.args['username']}', '{self.args['email']}', '{self.args['password']}', NULL);"
        )

    def __check_user_query(self):
        """
        Generates a SQL query to check if a user exists by username or email.

        Returns:
            str: SQL query to select a user by username or email.
        """
        return (
            "SELECT * FROM Users "
            f"WHERE username='{self.args['username']}' OR email='{self.args['email']}';"
        )

    def __view_results_query(self):
        """
        Generates a SQL query to view the results of a specified election.

        Returns:
            str: SQL query to count votes for each candidate in an election.
        """
        return f"""
            SELECT 
                e.name AS election_name,
                c.name AS candidate_name,
                COUNT(v.id) AS vote_count
            FROM 
                Elections e
            JOIN 
                Candidates c ON e.id = c.election_id
            LEFT JOIN 
                Votes v ON c.id = v.candidate_id
            WHERE 
                e.name = '{self.args['election_name']}'
            GROUP BY 
                e.name, c.name
            ORDER BY 
                vote_count DESC, candidate_name ASC;
            """

    def __list_elections_query(self):
        """
        Generates a SQL query to list all elections.

        Returns:
            str: SQL query to retrieve all records from the Elections table.
        """
        return "SELECT * FROM Elections;"

    def __check_vote_query(self):
        """
        Generates a SQL query to check if a user has voted in a specific election.

        Returns:
            str: SQL query to check vote existence for a user and election.
        """
        return f"""
            SELECT EXISTS (
                SELECT 1 
                FROM Votes v
                JOIN Elections e ON v.election_id = e.id
                WHERE v.username = '{self.args["username"]}' 
                  AND e.name = '{self.args["election_name"]}'
            ) AS has_voted;
            """

    def __vote_query(self):
        """
        Generates a SQL query to register a user's vote in a specified election.

        Returns:
            str: SQL query to insert a vote for the specified user and candidate.
        """
        return f"""
            INSERT INTO Votes (username, election_id, candidate_id, vote_time)
            SELECT '{self.args["username"]}', e.id, c.id, CURRENT_TIMESTAMP
            FROM Elections e
            JOIN Candidates c ON c.election_id = e.id
            WHERE e.name = '{self.args["election_name"]}'
              AND c.name = '{self.args["candidate_name"]}';
            """

    def __check_election_query(self):
        """
        Generates a SQL query to check if an election exists by name.

        Returns:
            str: SQL query to check if an election record exists by name.
        """
        return f"""
            SELECT EXISTS (
                SELECT 1
                FROM Elections
                WHERE name = '{self.args["election_name"]}'
            ) AS election_exists;
            """

    def __create_election(self):
        """
        Generates SQL query to create a new election.
        Returns:
            str: SQL query to insert the new election.
        """
        # Format the dates to ensure they are valid datetime values
        start_date = Query.__format_date(self.args["start_date"])
        end_date = Query.__format_date(self.args["end_date"])

        # Insert the new election
        return f"""
            INSERT INTO Elections (name, description, start_time, end_time, creator_username)
            VALUES ('{self.args['election_name']}', '{self.args['election_description']}', 
                    '{start_date}', '{end_date}', '{self.args['creator_username']}');
            """

    def __insert_candidates(self):
        """
        Generates SQL queries to add new candidates to an election.
        Returns:
            str: SQL query to insert the new candidates.
        """

        candidates_insert = (
            "INSERT INTO Candidates (name, birth_date, occupation, program, election_id) VALUES\n"
            + ",\n".join(
                f"('{candidate['name']}', '{Query.__format_date(candidate['birth_date'])}','{candidate['occupation']}', '{candidate['program']}', {self.args['election_id']})"
                for candidate in self.args["candidates"]
            )
            + ";"
        )

        return candidates_insert

    @staticmethod
    def __format_date(date_str):
        """
        Formats the given date string to ensure it is in the correct datetime format for SQL.

        Args:
            date_str (str): The date string to format.

        Returns:
            str: The formatted date string as 'YYYY-MM-DD HH:MM:SS'.
        """

        try:
            # If the input date string is valid, append time to it
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            return date.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError as exc:
            raise ValueError(
                f"Incorrect date format for: {date_str}. Expected format: YYYY-MM-DD"
            ) from exc
