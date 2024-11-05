"""Module to define the GUI of the election app"""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

from tkcalendar import Calendar

from tools.api_connector import APIConnector


class ElectionApp:
    """
    ElectionApp is the main GUI class for the Election Application.
    It provides a login screen and navigation options for registering,
    logging in, and viewing election results.

    Attributes:
        api_connector (APIConnector): An instance of the APIConnector class to handle API calls.
        root (tk.Tk): The main Tkinter window for the application.
    """

    def __init__(self):
        """
        Initializes the ElectionApp class.

        Sets up the Tkinter window and login UI elements, including entry fields
        for username and password, and buttons for login, registration, and results view.
        """
        # Initialize the api_connector for API interactions
        self.api_connector = APIConnector(api_route="http://localhost:8080")

        self.api_connector.check_health()

        # Set up the main Tkinter window
        self.root = tk.Tk()
        self.root.title("Election App")
        self.root.geometry("500x250")

        # Login UI elements
        # Label and entry for User ID
        tk.Label(self.root, text="Userid:").pack(pady=10)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        # Label and entry for Password (masked with '*')
        tk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        # Button to trigger login validation
        tk.Button(self.root, text="Login", command=self.validate_login).pack(pady=5)

        # Button to open the registration screen
        tk.Button(self.root, text="Register", command=self.show_register_screen).pack(
            pady=5
        )

        # Button to open the results viewer window
        tk.Button(
            self.root,
            text="View Results",
            command=lambda: ResultsViewer(self.root, self.api_connector).show(),
        ).pack(pady=5)

    def run(self):
        """
        Runs the main Tkinter event loop.

        This method starts the Tkinter mainloop, keeping the window open
        until the user closes it.
        """
        self.root.mainloop()

    def validate_login(self):
        """
        Validates the user's login credentials.

        Retrieves the username and password from the input fields and sends
        them to the APIConnector for verification. If the credentials are valid,
        it proceeds to the main screen. If invalid, it shows an error message.
        """
        # Get username and password from input fields
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Check credentials via the APIConnector's login API
        if self.api_connector(
            process="login",
            values={
                "username": username,
                "password": password,
            },
        ):
            # If login is successful, save the username in the api_connector and show the main screen
            self.api_connector.user_logged_in = username
            MainScreen(self.root, self.api_connector).show()
        else:
            # Show an error message if login fails
            messagebox.showerror("Login Failed", "Invalid username or password")

    def show_register_screen(self):
        """
        Opens the registration window.

        This method opens a new window where users can register by creating
        a new account. The registration screen is managed by the RegisterWindow class.
        """
        RegisterWindow(self.root, self.api_connector).show()


class RegisterWindow:
    """
    RegisterWindow creates a registration form in a new top-level window.
    It allows users to enter a username, email, and password to register
    a new account.

    Attributes:
        api_connector (APIConnector): An instance of the APIConnector class to handle API calls.
        window (tk.Toplevel): The registration window displayed to the user.
    """

    def __init__(self, parent, api_connector):
        """
        Initializes the RegisterWindow class.

        Args:
            parent (tk.Tk or tk.Toplevel): The parent window that owns this registration window.
            api_connector (APIConnector): The api_connector instance used for API calls to register a new user.
        """
        # Store the api_connector instance for making API requests
        self.api_connector = api_connector

        # Create a new top-level window for registration
        self.window = tk.Toplevel(parent)
        self.window.title("Registration")
        self.window.geometry("250x250")

        # User ID input
        tk.Label(self.window, text="Userid:").pack()
        self.username_entry = tk.Entry(self.window)
        self.username_entry.pack()

        # Email input
        tk.Label(self.window, text="Email:").pack()
        self.email_entry = tk.Entry(self.window)
        self.email_entry.pack()

        # Password input (masked with '*')
        tk.Label(self.window, text="Password:").pack()
        self.password_entry = tk.Entry(self.window, show="*")
        self.password_entry.pack()

        # Register button that triggers the register_user method
        tk.Button(self.window, text="Register", command=self.register_user).pack(
            pady=20
        )

    def register_user(self):
        """
        Registers a new user by sending the entered details to the API.

        Collects the username, email, and password from the input fields
        and sends them to the api_connector for registration. If successful,
        displays a success message and closes the window. If registration
        fails, shows an error message.
        """
        # Retrieve input values from the entry fields
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()

        # Attempt to register the user with the api_connector
        if self.api_connector(
            process="register",
            values={
                "username": username,
                "email": email,
                "password": password,
            },
        ):
            # If registration is successful, show a confirmation and close the window
            messagebox.showinfo(
                "Success", "Registration successful. Please close this window."
            )
            self.window.destroy()
        else:
            # Show an error if the registration fails (e.g., username or email exists)
            messagebox.showerror("Error", "Username or email already exists.")

    def show(self):
        """
        Displays the registration window and prevents interaction
        with other windows until it is closed.

        This method uses the `grab_set` method to make the registration
        window modal.
        """
        self.window.grab_set()


class MainScreen:
    """
    MainScreen displays the main dashboard for the logged-in user.
    It provides options to create an election, vote, and view results.

    Attributes:
        api_connector (APIConnector): An instance of the APIConnector class representing the logged-in user.
        window (tk.Toplevel): The main application window shown after login.
    """

    def __init__(self, parent, api_connector):
        """
        Initializes the MainScreen class.

        Args:
            parent (tk.Tk or tk.Toplevel): The parent window that this main screen will replace.
            api_connector (APIConnector): The api_connector instance representing the logged-in user.
        """
        # Store the api_connector instance for managing the user's session and actions
        self.api_connector = api_connector

        # Create a new top-level window for the main application screen
        self.window = tk.Toplevel(parent)
        self.window.title(f"Election App - {self.api_connector.user_logged_in}")
        self.window.geometry("500x250")

        # Hide the parent window (typically the login window)
        parent.withdraw()

        # Set up protocol to handle window close event
        self.window.protocol("WM_DELETE_WINDOW", self.close)

        # Main screen UI elements
        # Label displaying a welcome message
        tk.Label(self.window, text="Select an option").pack(pady=(30, 10))

        # Button to create a new election, opens NewElectionScreen
        tk.Button(
            self.window,
            text="Create Election",
            command=lambda: NewElectionScreen(self.window, self.api_connector).show(),
        ).pack(pady=10)

        # Button to open the voting window, opens VoteWindow
        tk.Button(
            self.window,
            text="Vote",
            command=lambda: VoteWindow(self.window, self.api_connector).show(),
        ).pack()

        # Button to view election results, opens ResultsViewer
        tk.Button(
            self.window,
            text="View Results",
            command=lambda: ResultsViewer(self.window, self.api_connector).show(),
        ).pack(pady=10)

    def close(self):
        """
        Closes the main screen window and logs out the user.

        This method destroys the main screen window, logs out the user
        by resetting `user_logged_in` in the api_connector, and restarts the
        ElectionApp to show the login screen again.
        """
        # Destroy the main screen window
        self.window.destroy()

        # Log out the user by resetting the logged-in user attribute
        self.api_connector.user_logged_in = None

        # Restart the application by re-initializing ElectionApp
        ElectionApp().run()

    def show(self):
        """
        Displays the main screen window and prevents interaction
        with other windows until it is closed.

        This method uses the `grab_set` method to make the main screen
        window modal.
        """
        self.window.grab_set()


class NewElectionScreen:
    """
    A GUI for creating a new election, allowing users to input election details,
    manage candidate information, and submit the election data.

    This screen provides fields for the election's name, description, start and end dates,
    and candidate information including name, birth date, occupation, and program.
    It also features a calendar pop-up for date selection and validation for input data.

    Attributes:
        api_connector: The api_connector instance used to communicate with the backend server.
        window: The main window for this screen, allowing user interaction.
        candidates: A list to store candidate details.
    """

    def __init__(self, parent, api_connector):
        """
        Initializes the NewElectionScreen with the given parent window and api_connector.

        Args:
            parent: The parent window that this screen will be a child of.
            api_connector: An instance of the api_connector used for backend interactions.
        """
        self.api_connector = api_connector
        self.window = tk.Toplevel(parent)  # Create a new top-level window
        self.window.title("Create New Election")  # Set the window title
        self.window.geometry("600x600")  # Set the window size

        # Store candidates in a list
        self.candidates = []

        # Frame for entering election name and description
        election_info_frame = tk.Frame(self.window)
        election_info_frame.pack(pady=(10, 5))

        tk.Label(election_info_frame, text="Name of the election:").grid(
            row=0, column=0, padx=(0, 10)
        )
        self.election_name_entry = tk.Entry(
            election_info_frame
        )  # Entry for election name
        self.election_name_entry.grid(row=1, column=0, padx=(0, 10))

        tk.Label(election_info_frame, text="Description of the election:").grid(
            row=0, column=1, padx=(10, 0)
        )
        self.election_description_entry = tk.Entry(
            election_info_frame
        )  # Entry for election description
        self.election_description_entry.grid(row=1, column=1, padx=(10, 0))

        # Frame for date pickers (start and end date on the same row)
        date_frame = tk.Frame(self.window)
        date_frame.pack(pady=(10, 5))

        tk.Label(date_frame, text="Start Date:").grid(row=0, column=0, padx=(0, 10))
        self.start_date_entry = tk.Entry(date_frame)  # Entry for start date
        self.start_date_entry.grid(row=1, column=0, padx=(0, 10))
        self.start_date_entry.bind(
            "<Button-1>",
            lambda event: self.open_calendar(
                self.start_date_entry
            ),  # Open calendar on click
        )

        tk.Label(date_frame, text="End Date:").grid(row=0, column=1, padx=(10, 0))
        self.end_date_entry = tk.Entry(date_frame)  # Entry for end date
        self.end_date_entry.grid(row=1, column=1, padx=(10, 0))
        self.end_date_entry.bind(
            "<Button-1>",
            lambda event: self.open_calendar(
                self.end_date_entry
            ),  # Open calendar on click
        )

        # Section for adding candidates
        tk.Label(self.window, text="Add Candidate Information").pack(pady=(20, 5))

        # Frame for candidate name and birth date on the same row
        candidate_row1 = tk.Frame(self.window)
        candidate_row1.pack(pady=(5, 0))

        tk.Label(candidate_row1, text="Candidate Name:").grid(
            row=0, column=0, padx=(0, 10)
        )
        self.candidate_name_entry = tk.Entry(candidate_row1)  # Entry for candidate name
        self.candidate_name_entry.grid(row=1, column=0, padx=(0, 10))

        tk.Label(candidate_row1, text="Birth Date:").grid(row=0, column=1, padx=(10, 0))
        self.candidate_birth_date_entry = tk.Entry(
            candidate_row1
        )  # Entry for candidate birth date
        self.candidate_birth_date_entry.grid(row=1, column=1, padx=(10, 0))
        self.candidate_birth_date_entry.bind(
            "<Button-1>",
            lambda event: self.open_calendar(
                self.candidate_birth_date_entry
            ),  # Open calendar on click
        )

        # Frame for candidate occupation and program on the same row
        candidate_row2 = tk.Frame(self.window)
        candidate_row2.pack(pady=(5, 10))

        tk.Label(candidate_row2, text="Occupation:").grid(row=0, column=0, padx=(0, 10))
        self.candidate_occupation_entry = tk.Entry(
            candidate_row2
        )  # Entry for candidate occupation
        self.candidate_occupation_entry.grid(row=1, column=0, padx=(0, 10))

        tk.Label(candidate_row2, text="Program:").grid(row=0, column=1, padx=(10, 0))
        self.candidate_program_entry = tk.Entry(
            candidate_row2
        )  # Entry for candidate program
        self.candidate_program_entry.grid(row=1, column=1, padx=(10, 0))

        # Button to add candidate
        tk.Button(self.window, text="Add Candidate", command=self.add_candidate).pack(
            pady=(10, 20)  # Button for adding a candidate
        )

        # Table headers for displaying candidates
        self.candidate_table_frame = tk.Frame(self.window)
        self.candidate_table_frame.pack(pady=10)

        headers = [
            "Name",
            "Birth Date",
            "Occupation",
            "Program",
        ]  # Candidate table headers
        for i, header in enumerate(headers):
            tk.Label(
                self.candidate_table_frame, text=header, font=("Arial", 10, "bold")
            ).grid(
                row=0, column=i, padx=5, pady=5
            )  # Set header labels

        # Track candidate rows to display in the table
        self.candidate_rows = 1  # Start from row 1 (row 0 is headers)

        # Submit button to create the election
        tk.Button(
            self.window, text="Create Election", command=self.create_election
        ).pack(
            pady=20
        )  # Button to create the election

    def open_calendar(self, date_entry):
        """Opens a pop-up calendar for date selection.

        Args:
            date_entry: The Entry widget where the selected date will be inserted.
        """
        calendar_window = tk.Toplevel(
            self.window
        )  # Create a new top-level window for the calendar
        calendar_window.title("Select Date")  # Set the calendar window title
        calendar_window.geometry("300x300")  # Set the calendar window size
        calendar_window.transient(
            self.window
        )  # Make the calendar window a transient window
        calendar_window.grab_set()  # Grab focus to this window

        # Calendar widget in the pop-up
        calendar = Calendar(
            calendar_window, selectmode="day", date_pattern="y-mm-dd"
        )  # Create calendar
        calendar.pack(pady=20)  # Pack calendar in the window

        # When a date is selected in the calendar
        def on_date_select(event):
            selected_date = calendar.get_date()  # Get selected date
            date_entry.delete(0, tk.END)  # Clear the entry
            date_entry.insert(0, selected_date)  # Insert the selected date
            calendar_window.destroy()  # Close the calendar window

        calendar.bind(
            "<<CalendarSelected>>", on_date_select
        )  # Bind date selection event

    def add_candidate(self):
        """Adds a candidate's details to the list and updates the display.

        Validates that all required fields are filled before adding the candidate.
        """
        name = self.candidate_name_entry.get()  # Get candidate name
        birth_date = self.candidate_birth_date_entry.get()  # Get candidate birth date
        occupation = self.candidate_occupation_entry.get()  # Get candidate occupation
        program = self.candidate_program_entry.get()  # Get candidate program

        # Validate that all fields are filled
        if not name or not birth_date or not occupation or not program:
            messagebox.showerror(
                "Error", "Please fill in all candidate details."
            )  # Show error if fields are empty
            return

        # Add candidate to list and display in table
        candidate = {
            "name": name,
            "birth_date": birth_date,
            "occupation": occupation,
            "program": program,
        }
        self.candidates.append(candidate)  # Append candidate to the candidates list

        # Display candidate in the table
        tk.Label(self.candidate_table_frame, text=name).grid(
            row=self.candidate_rows, column=0, padx=5, pady=5  # Display candidate name
        )
        tk.Label(self.candidate_table_frame, text=birth_date).grid(
            row=self.candidate_rows,
            column=1,
            padx=5,
            pady=5,  # Display candidate birth date
        )
        tk.Label(self.candidate_table_frame, text=occupation).grid(
            row=self.candidate_rows,
            column=2,
            padx=5,
            pady=5,  # Display candidate occupation
        )
        tk.Label(self.candidate_table_frame, text=program).grid(
            row=self.candidate_rows,
            column=3,
            padx=5,
            pady=5,  # Display candidate program
        )

        # Move to the next row for the next candidate
        self.candidate_rows += 1

        # Clear entry fields after adding
        self.candidate_name_entry.delete(0, tk.END)
        self.candidate_birth_date_entry.delete(0, tk.END)
        self.candidate_occupation_entry.delete(0, tk.END)
        self.candidate_program_entry.delete(0, tk.END)

    def create_election(self):
        """Creates an election with the provided details and candidates.

        Validates all input fields and ensures at least one candidate is present.
        Displays appropriate error messages if validation fails.
        """
        # Check if there is at least one candidate
        if not self.candidates:
            messagebox.showerror(
                "Error", "At least 1 candidate is required"
            )  # Show error if no candidates
            return

        # Collect election details
        election_details = {
            "candidates": self.candidates,
            "election_name": self.election_name_entry.get(),
            "election_description": self.election_description_entry.get(),
            "start_date": self.start_date_entry.get(),
            "end_date": self.end_date_entry.get(),
            "creator_username": self.api_connector.user_logged_in,  # Get username from api_connector
        }

        # Ensure all fields are filled
        if not all(election_details.values()):
            messagebox.showerror(
                "Error", "Fill out all the fields."
            )  # Show error if fields are empty
            return

        # Check if end date is after start date
        try:
            start_date = datetime.strptime(
                election_details["start_date"], "%Y-%m-%d"
            )  # Parse start date
            end_date = datetime.strptime(
                election_details["end_date"], "%Y-%m-%d"
            )  # Parse end date

            if end_date <= start_date:
                messagebox.showerror(
                    "Error", "End date must be after start date."
                )  # Show error if dates are invalid
                return
        except ValueError:
            messagebox.showerror(
                "Error",
                "Please enter dates in the format YYYY-MM-DD.",  # Show error for date format
            )
            return

        # Attempt to create the election
        if self.api_connector(
            process="create_election", values=election_details
        ):  # Call api_connector to create election
            messagebox.showinfo(
                "Success", "The election was created successfully!"
            )  # Show success message
        else:
            messagebox.showerror(
                "Error",
                f"Election with the name {election_details['election_name']} exists.",  # Show error if election exists
            )

    def show(self):
        """Displays the election screen and makes it the active window."""
        self.window.grab_set()  # Set focus to this window


class ResultsViewer:
    """
    A GUI for viewing election results and details.

    This class provides a user interface for selecting an election from a list,
    viewing its details, and displaying the results of the selected election.

    Attributes:
        api_connector: The api_connector instance used to communicate with the backend server.
        window: The main window for this screen, allowing user interaction.
        election_details: A list of details for all available elections.
        selected_election: A StringVar to hold the currently selected election.
        details_label_widgets: A dictionary mapping election detail keys to their label widgets.
        tree: A Treeview widget to display the results of the selected election.
    """

    def __init__(self, parent, api_connector):
        """
        Initializes the ResultsViewer with the given parent window and api_connector.

        Args:
            parent: The parent window that this screen will be a child of.
            api_connector: An instance of the api_connector used for backend interactions.
        """
        self.api_connector = (
            api_connector  # Store the api_connector instance for backend communication
        )
        self.window = tk.Toplevel(parent)  # Create a new top-level window
        self.window.title("Election Results")  # Set the window title
        self.window.geometry("1000x600")  # Set the window size

        tk.Label(self.window, text="Please select one of the elections:").pack(pady=10)

        # Get election names for dropdown
        election_details = api_connector(
            process="list_elections",
        )  # Fetch list of elections
        self.election_details = election_details  # Store election details for later use
        elections = [election["name"] for election in election_details]  # Extract names

        # Variable to hold the selected election name
        self.selected_election = tk.StringVar(self.window)
        self.selected_election.set(elections[0])  # Set default selection

        # Create a dropdown menu for selecting elections
        tk.OptionMenu(self.window, self.selected_election, *elections).pack()
        # Button to view results for the selected election
        tk.Button(self.window, text="View results", command=self.get_results).pack(
            pady=10
        )

        # Create a frame for displaying election details
        self.details_frame = tk.Frame(self.window)
        self.details_frame.pack(pady=10)

        # Define the static labels and corresponding keys for election info
        self.details_labels = [
            "ID",
            "Name",
            "Description",
            "Creator",
            "Start Time",
            "End Time",
        ]
        self.details_keys = [
            "id",
            "name",
            "description",
            "creator_username",
            "start_time",
            "end_time",
        ]

        # Create a static table for election details with placeholders
        self.details_label_widgets = {}
        for i, label in enumerate(self.details_labels):
            tk.Label(self.details_frame, text=f"{label}:").grid(
                row=i, column=0, padx=5, sticky=tk.W
            )
            label_value = tk.Label(
                self.details_frame, text=""
            )  # Placeholder label for details
            label_value.grid(row=i, column=1, padx=5, sticky=tk.W)
            self.details_label_widgets[self.details_keys[i]] = (
                label_value  # Map keys to label widgets
            )

        # Set up results table
        columns = ("Candidate", "Election", "Votes")  # Define columns for results table
        self.tree = ttk.Treeview(self.window, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)  # Set column headings

        # Set column widths
        self.tree.column("Candidate", anchor=tk.W, width=250)
        self.tree.column("Election", anchor=tk.W, width=250)
        self.tree.column("Votes", anchor=tk.CENTER, width=100)

        # Pack the treeview widget
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add a scrollbar for the Treeview
        scrollbar = ttk.Scrollbar(
            self.window, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscroll=scrollbar.set)  # Link scrollbar to treeview
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def get_results(self):
        """Fetches and displays results for the selected election.

        This method retrieves the results from the server and populates the
        results Treeview with candidate names, election names, and vote counts.
        It also updates the details section with information about the selected election.
        """
        selected_election_name = (
            self.selected_election.get()
        )  # Get the currently selected election name
        results = self.api_connector(
            process="view_results",
            values={
                "election_name": selected_election_name,
            },
        )  # Fetch results for the selected election

        # Clear existing data in the treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Populate the Treeview with the new results
        for entry in results:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    entry["candidate_name"],
                    entry["election_name"],
                    entry["vote_count"],
                ),
            )

        # Retrieve and display election info for the selected election
        selected_election_info = next(
            (
                election
                for election in self.election_details
                if election["name"] == selected_election_name
            ),
            None,
        )

        # Update the details labels with information from the selected election
        if selected_election_info:
            for key, label_widget in self.details_label_widgets.items():
                label_widget.config(
                    text=selected_election_info.get(key, "")
                )  # Update label text

    def show(self):
        """Displays the results viewer window and makes it the active window."""
        self.window.grab_set()  # Set focus to this window


class VoteWindow:
    """
    A GUI for casting votes in an election.

    This class provides an interface for users to select an election,
    choose a candidate, and submit their vote.

    Attributes:
        api_connector: The api_connector instance used to communicate with the backend server.
        window: The main window for this voting interface.
        selected_election: A StringVar to hold the currently selected election name.
        selected_candidate: A StringVar to hold the currently selected candidate name.
        candidate_menu: The dropdown menu for selecting candidates.
    """

    def __init__(self, parent, api_connector):
        """
        Initializes the VoteWindow with the given parent window and api_connector.

        Args:
            parent: The parent window that this voting interface will belong to.
            api_connector: An instance of the api_connector used for backend interactions.
        """
        self.api_connector = (
            api_connector  # Store the api_connector instance for backend communication
        )
        self.window = tk.Toplevel(parent)  # Create a new top-level window for voting
        self.window.title(
            f"Vote as {self.api_connector.user_logged_in}"
        )  # Set the window title
        self.window.geometry("500x250")  # Set the size of the voting window

        # Label prompting the user to select an election
        tk.Label(self.window, text="Please select an election").pack(pady=(30, 0))

        # Retrieve the list of live elections from the backend
        elections = [e["name"] for e in api_connector(process="list_live_elections")]
        self.selected_election = tk.StringVar(
            self.window
        )  # Variable to store the selected election
        self.selected_election.set(
            elections[0]
        )  # Set default selection to the first election

        # Dropdown menu for selecting an election, with a command to update candidates
        tk.OptionMenu(
            self.window,
            self.selected_election,
            *elections,
            command=self.update_candidates,
        ).pack(pady=(10, 10))

        # Variable to store the selected candidate
        self.selected_candidate = tk.StringVar(self.window)
        # Dropdown menu for selecting candidates, initially empty
        self.candidate_menu = tk.OptionMenu(self.window, self.selected_candidate, "")
        self.candidate_menu.pack()

        # Button to submit the vote
        tk.Button(self.window, text="Vote", command=self.submit_vote).pack(pady=20)

    def update_candidates(self, selected_election):
        """Updates the candidate dropdown based on the selected election.

        This method retrieves the list of candidates for the selected election
        and updates the candidates dropdown menu accordingly.

        Args:
            selected_election: The name of the election for which to update candidates.
        """
        # Retrieve the candidates for the selected election from the backend
        candidates = [
            c["name"]
            for c in self.api_connector(
                process="list_election_candidates",
                values={
                    "election_name": selected_election,
                },
            )
        ]
        # Set the selected candidate to the first candidate if available
        self.selected_candidate.set(candidates[0] if candidates else "")
        # Clear the current candidate menu
        self.candidate_menu["menu"].delete(0, "end")
        # Add candidates to the dropdown menu
        for candidate in candidates:
            self.candidate_menu["menu"].add_command(
                label=candidate, command=tk._setit(self.selected_candidate, candidate)
            )

    def submit_vote(self):
        """Submits the user's vote for the selected candidate in the selected election.

        This method retrieves the currently selected election and candidate,
        and attempts to submit the vote to the backend. It displays a message
        indicating whether the vote was successful or failed.

        If the vote is successful, the voting window is closed.
        """
        election = self.selected_election.get()  # Get the currently selected election
        candidate = (
            self.selected_candidate.get()
        )  # Get the currently selected candidate

        # Submit the vote to the backend
        if self.api_connector(
            process="vote",
            values={
                "username": self.api_connector.user_logged_in,
                "election_name": election,
                "candidate_name": candidate,
            },
        ):
            # Show a success message if the vote was submitted successfully
            messagebox.showinfo(
                "Vote Successful", f"Successfully voted for {candidate} in {election}."
            )
            self.window.destroy()  # Close the voting window
        else:
            # Show a warning message if the user has already voted in this election
            messagebox.showwarning(
                "Vote Failed", "You have already voted in this election."
            )

    def show(self):
        """Displays the voting window and makes it the active window."""
        self.window.grab_set()  # Set focus to this window, preventing interaction with others


# Running the Election App
if __name__ == "__main__":
    app = ElectionApp()
    app.run()
