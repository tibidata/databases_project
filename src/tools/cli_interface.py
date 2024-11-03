import os

from tools.db_client import DBClient


class CLIInterface:

    def __init__(self, api_route: str) -> None:

        self.user_logged_in = False

        self.db_client = DBClient(api_route=api_route)

    def __call__(self, **kwargs):

        CLIInterface.__clear_screen()

        self.db_client.check_health()

        while True:

            if self.login():
                break

        while True:

            if self.main_screen():
                break

    def login(self):

        while True:

            CLIInterface.__clear_screen()

            CLIInterface.__print_menu(menu_type="login")

            choice = input("Enter selection\n")

            if choice == "1":

                CLIInterface.__clear_screen()

                login_id = input("Enter login ID\n")
                password = input("Enter password\n")

                if self.__validate_login(
                    login_id=login_id,
                    password=password,
                ):

                    input("Login successful...press enter to continue")

                    self.user_logged_in = True

                    return True

                input("Login ID or password incorrect...press enter to continue")

                return False

            elif choice == "2":

                CLIInterface.__clear_screen()

                login_id = input("Enter login ID\n")
                password = input("Enter password\n")

                self.__register_user(login_id=login_id, password=password)

                input(
                    "Registration successful...press enter to return to the main screen"
                )

                return False

            elif choice == "3":

                CLIInterface.__clear_screen()

                poll_id = input("Please add the ID of the poll\n")

                self.__query_results(poll_id=poll_id)

            elif choice == "0":

                CLIInterface.__clear_screen()

                print("Exiting the application...")

                return True  # Exit the loop and end the program

            else:

                print("Invalid choice...please enter a valid option")

    def main_screen(self):

        while True:

            CLIInterface.__clear_screen()

            CLIInterface.__print_menu(menu_type="control")

            choice = input("Enter selection\n")

            if choice == "1":

                CLIInterface.__clear_screen()

                self.__list_polls()

                poll_id = input("Please select the ID of the poll: \n")

                participant_name = input(
                    "\nPlease add the name of the participiant: \n"
                )

                if self.__vote(poll_id=poll_id, participant_name=participant_name):

                    input("Successful vote...press enter to return to the main screen")

                return False

            elif choice == "2":
                # TODO: create poll

                CLIInterface.__clear_screen()

                poll_name = input("Please add a name to the new poll\n")

                participants = input(
                    "Please add the name of the participants separated be a comma. \nEXAMPLE:\nTest1, Test2, Test3\nParticipants:\n"
                )

                participants = [
                    participant.strip(" ")
                    for participant in participants.strip(",").split(",")
                ]

                print(participants)

                if self.__create_new_poll(
                    poll_name=poll_name, participants=participants
                ):

                    input(
                        "Poll created successfully...press enter to return to the main screen"
                    )

                return False

            elif choice == "0":

                CLIInterface.__clear_screen()

                print("Exiting the application...")

                return True  # Exit the loop and end the program

            else:

                print("Invalid choice...please enter a valid option")

    def __list_polls(self) -> bool:

        print("Polls here...")

    def __vote(self, **kwargs) -> bool:

        return True

    def __create_new_poll(self, **kwargs) -> bool:

        return True

    def __validate_login(self, **kwargs) -> bool:

        return True

    def __register_user(self, **kwargs) -> bool:

        return True

    def __query_results(self, **kwargs) -> bool:

        return True

    @staticmethod
    def __print_menu(**kwargs) -> None:

        if kwargs.get("menu_type") == "login":

            print(
                """\nMenu:
                  1. Login
                  2. Register
                  3. View results/standings
                  0. Exit
                  """
            )

        elif kwargs.get("menu_type") == "control":

            print(
                """\nMenu:
                1. Vote
                2. Create new poll
                0. Exit
                """
            )

    @staticmethod
    def __clear_screen():
        # Clear the terminal screen for Linux, macOS, and Windows
        os.system("cls" if os.name == "nt" else "clear")
