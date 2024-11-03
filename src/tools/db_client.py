import requests
import time


class DBClient:
    def __init__(self, api_route: str) -> None:
        self.api_route = api_route
        self.__load_ddl_commands(ddl_file_path="../DDL/ddl.txt")

    def __call__(self, **kwargs):
        return self.__query(**kwargs)

    def check_health(self):
        try:
            # Make a GET request to the health check endpoint
            hc_route = self.api_route + "/"
            response = requests.get(hc_route, timeout=5)

            # Check if the response was successful
            if response.status_code == 200:
                data = response.json()
                print("\nHealth Check Successful!")
                print("Message:", data.get("message"))
                print("Database:", data.get("database"))
                input("\nPress enter to continue...")
            else:
                print("\nHealth Check Failed. Status Code:", response.status_code)
                print("Response:", response.text)
                return True
        except requests.exceptions.RequestException as e:
            print("Error connecting to the Backend API:", e)
            return False

    def __load_ddl_commands(self, ddl_file_path: str) -> None:
        """
        Load DDL commands from a text file and send them to the Flask API for execution.
        This method will wait and retry if a command execution fails.

        :param ddl_file_path: Path to the text file containing DDL commands.
        """
        try:
            # Read DDL commands from the file
            with open(ddl_file_path, "r") as file:
                ddl_commands = file.read()

            # Split commands by semicolon and filter out any empty commands
            commands = [cmd.strip() for cmd in ddl_commands.split(";") if cmd.strip()]

            # Send each command to the Flask API
            for command in commands:

                payload = {"sql_command": command}
                response = requests.post(self.api_route + "/populate", json=payload)

                if response.status_code == 200:
                    print(f"Successfully executed command: {command}")
                    success = True
                else:
                    print(f"Failed to execute command: {command}.")
                    print("Status Code:", response.status_code)
                    print("Response:", response.text)

        except FileNotFoundError:
            print(f"Error: The file '{ddl_file_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def __query(self, **kwargs):
        # Placeholder for any other query logic you may want to implement
        pass
