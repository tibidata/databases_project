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

from tools.db_client import DBClient

import logging
from flask import Flask

app = Flask(__name__)

# Set up logging configuration
logging.basicConfig(
    filename="app.log",  # Name of the log file
    level=logging.INFO,  # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",  # Log format
    datefmt="%Y-%m-%d %H:%M:%S",  # Date format in the log file
)

# Log messages to verify
logging.info("Logging setup complete. Flask app has started.")

# Database configuration
db_config = {
    "host": os.getenv("MYSQL_HOST", "db"),
    "user": os.getenv("MYSQL_USER", "user"),
    "password": os.getenv("MYSQL_PASSWORD", "password"),
    "database": os.getenv("MYSQL_DATABASE", "testdb"),
}

db_client = DBClient()


@app.route("/")
def healthcheck():
    """
    Healthcheck endpoint to test the connection to the MySQL database.

    Returns:
        JSON: A message indicating successful connection or an error message.
    """

    return jsonify(db_client.check_health())


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

    query_params = {"query_type": data.get("process")}
    query_params.update(data.get("values"))

    logging.info(query_params)

    try:

        results = db_client(**query_params)

        logging.info(results)

        return jsonify({"response": results})

    except Exception as e:

        logging.error(e.with_traceback())


if __name__ == "__main__":
    # Run the Flask application on host 0.0.0.0 and port 5000
    app.run(host="0.0.0.0", port=5000)
