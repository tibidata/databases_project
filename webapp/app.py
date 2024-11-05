"""
A Flask application for querying a MySQL database via API endpoints.

This application provides two main routes:
1. Healthcheck (`/`): Verifies the connection to the MySQL database.
2. Query (`/query`): Executes SQL commands (SELECT, INSERT, UPDATE, DELETE) based on the JSON payload provided.

Environment Variables:
- MYSQL_HOST: Hostname of the MySQL database.
- MYSQL_USER: Username for the MySQL database.
- MYSQL_PASSWORD: Password for the MySQL database.
- MYSQL_DATABASE: Name of the database to connect to.

Requires:
- Flask: For the web server and routing.
- mysql.connector: For connecting to the MySQL database.
- logging: For logging incoming requests and errors.
"""

import os
import logging

from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

# Database configuration
db_config = {
    "host": os.getenv("MYSQL_HOST", "db"),
    "user": os.getenv("MYSQL_USER", "user"),
    "password": os.getenv("MYSQL_PASSWORD", "password"),
    "database": os.getenv("MYSQL_DATABASE", "testdb"),
}


@app.route("/")
def healthcheck():
    """
    Healthcheck endpoint to test the connection to the MySQL database.

    Returns:
        JSON: A message indicating successful connection or an error message.
    """
    try:
        # Establish database connection
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        database_name = cursor.fetchone()
        cursor.close()
        connection.close()
        return jsonify({"message": "Connected to MySQL!", "database": database_name})
    except mysql.connector.Error as err:
        # Return an error message in case of database connection failure
        return jsonify({"error": str(err)}), 500


@app.route("/query", methods=["POST"])
def query():
    """
    Execute a SQL query on the MySQL database.

    Expects JSON data with a key `sql_command` in the request body, which contains
    the SQL command to execute.

    Returns:
        JSON: Response containing either the result of a SELECT query or
              a success message for INSERT, UPDATE, or DELETE operations.
              Includes error details if an error occurs.
    """
    data = request.json
    logging.info(f"Received payload {data}")

    # Retrieve the SQL command from the request data
    sql_command = data.get("sql_command")

    if not sql_command:
        # Return an error if no SQL command is provided
        return jsonify({"error": "The 'sql_command' key is required."}), 400

    try:
        # Establish database connection
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Execute the SQL command
        cursor.execute(sql_command)

        # If the command is an INSERT, commit changes and retrieve the new record ID
        if sql_command.strip().lower().startswith("insert"):
            connection.commit()
            new_id = cursor.lastrowid
            response = {
                "response": "Record inserted successfully!",
                "command": sql_command,
                "new_record_id": new_id,
            }

        # For UPDATE or DELETE commands, commit changes and acknowledge success
        elif sql_command.strip().lower().startswith(("update", "delete")):
            connection.commit()
            response = {
                "response": "Command executed successfully!",
                "command": sql_command,
            }

        # For SELECT commands, fetch results and include them in the response
        else:
            result = cursor.fetchall()
            columns = (
                [desc[0] for desc in cursor.description] if cursor.description else []
            )
            response = {
                "response": "Query executed successfully!",
                "command": sql_command,
                "result": [dict(zip(columns, row)) for row in result],
            }

        cursor.close()
        connection.close()
        return jsonify(response)

    except mysql.connector.Error as err:
        # Return an error message if any MySQL error occurs during execution
        return jsonify({"error": str(err)}), 500


if __name__ == "__main__":
    # Run the Flask application on host 0.0.0.0 and port 5000
    app.run(host="0.0.0.0", port=5000)
