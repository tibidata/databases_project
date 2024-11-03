from flask import Flask, jsonify, request
import mysql.connector
import os

app = Flask(__name__)

# Database configuration
db_config = {
    'host': os.getenv('MYSQL_HOST', 'db'),
    'user': os.getenv('MYSQL_USER', 'user'),
    'password': os.getenv('MYSQL_PASSWORD', 'password'),
    'database': os.getenv('MYSQL_DATABASE', 'testdb')
}

@app.route("/")
def healthcheck():
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
        return jsonify({"error": str(err)}), 500

@app.route("/populate", methods=["POST"])
def populate():
    data = request.json  # Expecting JSON data in the request body with "sql_command" key
    sql_command = data.get("sql_command")

    if not sql_command:
        return jsonify({"error": "The 'sql_command' key is required."}), 400

    try:
        # Establish database connection
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Execute the SQL command
        cursor.execute(sql_command)

        # Commit changes if it’s an INSERT, UPDATE, DELETE command
        if sql_command.strip().lower().startswith(("insert", "update", "delete")):
            connection.commit()
            response = {"response": "Command executed successfully!", "command": sql_command}
        else:
            # For SELECT statements, fetch results
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            response = {
                "response": "Query executed successfully!",
                "command": sql_command,
                "result": [dict(zip(columns, row)) for row in result]
            }

        cursor.close()
        connection.close()
        return jsonify(response)

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)