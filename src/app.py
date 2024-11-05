import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

from tkcalendar import Calendar

from tools.db_client import DBClient


class ElectionApp:
    def __init__(self):
        self.client = DBClient(api_route="http://localhost:8080")
        self.root = tk.Tk()
        self.root.title("Election App")
        self.root.geometry("500x250")

        # Login Widgets
        tk.Label(self.root, text="Userid:").pack(pady=10)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        tk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        tk.Button(self.root, text="Login", command=self.validate_login).pack(pady=5)
        tk.Button(self.root, text="Register", command=self.show_register_screen).pack(
            pady=5
        )
        tk.Button(
            self.root,
            text="View Results",
            command=lambda: ResultsViewer(self.root, self.client).show(),
        ).pack(pady=5)

    def run(self):
        self.root.mainloop()

    def validate_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.client(query_type="login", username=username, password=password):
            self.client.user_logged_in = username
            MainScreen(self.root, self.client).show()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def show_register_screen(self):
        RegisterWindow(self.root, self.client).show()


class RegisterWindow:
    def __init__(self, parent, client):
        self.client = client
        self.window = tk.Toplevel(parent)
        self.window.title("Registration")
        self.window.geometry("250x250")

        tk.Label(self.window, text="Userid:").pack()
        self.username_entry = tk.Entry(self.window)
        self.username_entry.pack()

        tk.Label(self.window, text="Email:").pack()
        self.email_entry = tk.Entry(self.window)
        self.email_entry.pack()

        tk.Label(self.window, text="Password:").pack()
        self.password_entry = tk.Entry(self.window, show="*")
        self.password_entry.pack()

        tk.Button(self.window, text="Register", command=self.register_user).pack(
            pady=20
        )

    def register_user(self):
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()

        if self.client(
            query_type="register", username=username, email=email, password=password
        ):
            messagebox.showinfo(
                "Success", "Registration successful. Please close this window."
            )
            self.window.destroy()
        else:
            messagebox.showerror("Error", "Username or email already exists.")

    def show(self):
        self.window.grab_set()


class MainScreen:
    def __init__(self, parent, client):
        self.client = client
        self.window = tk.Toplevel(parent)
        self.window.title(f"Election App - {self.client.user_logged_in}")
        self.window.geometry("500x250")
        parent.withdraw()

        self.window.protocol("WM_DELETE_WINDOW", self.close)

        tk.Label(self.window, text="Select an option").pack(pady=(30, 10))
        tk.Button(
            self.window,
            text="Create Election",
            command=lambda: NewElectionScreen(self.window, self.client).show(),
        ).pack(pady=10)
        tk.Button(
            self.window,
            text="Vote",
            command=lambda: VoteWindow(self.window, self.client).show(),
        ).pack()
        tk.Button(
            self.window,
            text="View Results",
            command=lambda: ResultsViewer(self.window, self.client).show(),
        ).pack(pady=10)

    def close(self):
        self.window.destroy()
        self.client.user_logged_in = None
        ElectionApp().run()

    def show(self):
        self.window.grab_set()


class NewElectionScreen:
    def __init__(self, parent, client):
        self.client = client
        self.window = tk.Toplevel(parent)
        self.window.title("Create New Election")
        self.window.geometry("600x600")

        # Store candidates in a list
        self.candidates = []

        # Election name and description on the same row
        election_info_frame = tk.Frame(self.window)
        election_info_frame.pack(pady=(10, 5))

        tk.Label(election_info_frame, text="Name of the election:").grid(
            row=0, column=0, padx=(0, 10)
        )
        self.election_name_entry = tk.Entry(election_info_frame)
        self.election_name_entry.grid(row=1, column=0, padx=(0, 10))

        tk.Label(election_info_frame, text="Description of the election:").grid(
            row=0, column=1, padx=(10, 0)
        )
        self.election_description_entry = tk.Entry(election_info_frame)
        self.election_description_entry.grid(row=1, column=1, padx=(10, 0))

        # Frame for date pickers (start and end date on the same row)
        date_frame = tk.Frame(self.window)
        date_frame.pack(pady=(10, 5))

        tk.Label(date_frame, text="Start Date:").grid(row=0, column=0, padx=(0, 10))
        self.start_date_entry = tk.Entry(date_frame)
        self.start_date_entry.grid(row=1, column=0, padx=(0, 10))
        self.start_date_entry.bind(
            "<Button-1>", lambda event: self.open_calendar(self.start_date_entry)
        )

        tk.Label(date_frame, text="End Date:").grid(row=0, column=1, padx=(10, 0))
        self.end_date_entry = tk.Entry(date_frame)
        self.end_date_entry.grid(row=1, column=1, padx=(10, 0))
        self.end_date_entry.bind(
            "<Button-1>", lambda event: self.open_calendar(self.end_date_entry)
        )

        # Section for adding candidates
        tk.Label(self.window, text="Add Candidate Information").pack(pady=(20, 5))

        # Frame for candidate name and birth date on the same row
        candidate_row1 = tk.Frame(self.window)
        candidate_row1.pack(pady=(5, 0))

        tk.Label(candidate_row1, text="Candidate Name:").grid(
            row=0, column=0, padx=(0, 10)
        )
        self.candidate_name_entry = tk.Entry(candidate_row1)
        self.candidate_name_entry.grid(row=1, column=0, padx=(0, 10))

        tk.Label(candidate_row1, text="Birth Date:").grid(row=0, column=1, padx=(10, 0))
        self.candidate_birth_date_entry = tk.Entry(candidate_row1)
        self.candidate_birth_date_entry.grid(row=1, column=1, padx=(10, 0))
        self.candidate_birth_date_entry.bind(
            "<Button-1>",
            lambda event: self.open_calendar(self.candidate_birth_date_entry),
        )

        # Frame for candidate occupation and program on the same row
        candidate_row2 = tk.Frame(self.window)
        candidate_row2.pack(pady=(5, 10))

        tk.Label(candidate_row2, text="Occupation:").grid(row=0, column=0, padx=(0, 10))
        self.candidate_occupation_entry = tk.Entry(candidate_row2)
        self.candidate_occupation_entry.grid(row=1, column=0, padx=(0, 10))

        tk.Label(candidate_row2, text="Program:").grid(row=0, column=1, padx=(10, 0))
        self.candidate_program_entry = tk.Entry(candidate_row2)
        self.candidate_program_entry.grid(row=1, column=1, padx=(10, 0))

        # Button to add candidate
        tk.Button(self.window, text="Add Candidate", command=self.add_candidate).pack(
            pady=(10, 20)
        )

        # Table headers for candidate display
        self.candidate_table_frame = tk.Frame(self.window)
        self.candidate_table_frame.pack(pady=10)

        headers = ["Name", "Birth Date", "Occupation", "Program"]
        for i, header in enumerate(headers):
            tk.Label(
                self.candidate_table_frame, text=header, font=("Arial", 10, "bold")
            ).grid(row=0, column=i, padx=5, pady=5)

        # Track candidate rows to display in the table
        self.candidate_rows = 1  # Start from row 1 (row 0 is headers)

        # Submit button to create the election
        tk.Button(
            self.window, text="Create Election", command=self.create_election
        ).pack(pady=20)

    def open_calendar(self, date_entry):
        """Opens a pop-up calendar for date selection."""
        calendar_window = tk.Toplevel(self.window)
        calendar_window.title("Select Date")
        calendar_window.geometry("300x300")
        calendar_window.transient(self.window)
        calendar_window.grab_set()

        # Calendar widget in the pop-up
        calendar = Calendar(calendar_window, selectmode="day", date_pattern="y-mm-dd")
        calendar.pack(pady=20)

        # When a date is selected in the calendar
        def on_date_select(event):
            selected_date = calendar.get_date()
            date_entry.delete(0, tk.END)
            date_entry.insert(0, selected_date)
            calendar_window.destroy()

        calendar.bind("<<CalendarSelected>>", on_date_select)

    def add_candidate(self):
        """Adds a candidate's details to the list."""
        name = self.candidate_name_entry.get()
        birth_date = self.candidate_birth_date_entry.get()
        occupation = self.candidate_occupation_entry.get()
        program = self.candidate_program_entry.get()

        # Validate that all fields are filled
        if not name or not birth_date or not occupation or not program:
            messagebox.showerror("Error", "Please fill in all candidate details.")
            return

        # Add candidate to list and display in table
        candidate = {
            "name": name,
            "birth_date": birth_date,
            "occupation": occupation,
            "program": program,
        }
        self.candidates.append(candidate)

        # Display candidate in the table
        tk.Label(self.candidate_table_frame, text=name).grid(
            row=self.candidate_rows, column=0, padx=5, pady=5
        )
        tk.Label(self.candidate_table_frame, text=birth_date).grid(
            row=self.candidate_rows, column=1, padx=5, pady=5
        )
        tk.Label(self.candidate_table_frame, text=occupation).grid(
            row=self.candidate_rows, column=2, padx=5, pady=5
        )
        tk.Label(self.candidate_table_frame, text=program).grid(
            row=self.candidate_rows, column=3, padx=5, pady=5
        )

        # Move to the next row for the next candidate
        self.candidate_rows += 1

        # Clear entry fields after adding
        self.candidate_name_entry.delete(0, tk.END)
        self.candidate_birth_date_entry.delete(0, tk.END)
        self.candidate_occupation_entry.delete(0, tk.END)
        self.candidate_program_entry.delete(0, tk.END)

    def create_election(self):
        # Check if there is at least one candidate
        if not self.candidates:
            messagebox.showerror("Error", "At least 1 candidate is required")
            return

        # Collect election details
        election_details = {
            "query_type": "create_election",
            "candidates": self.candidates,
            "election_name": self.election_name_entry.get(),
            "election_description": self.election_description_entry.get(),
            "start_date": self.start_date_entry.get(),
            "end_date": self.end_date_entry.get(),
            "creator_username": self.client.user_logged_in,
        }

        # Ensure all fields are filled
        if not all(election_details.values()):
            messagebox.showerror("Error", "Fill out all the fields.")
            return

        # Check if end date is after start date
        try:
            start_date = datetime.strptime(election_details["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(election_details["end_date"], "%Y-%m-%d")

            if end_date <= start_date:
                messagebox.showerror("Error", "End date must be after start date.")
                return
        except ValueError:
            messagebox.showerror(
                "Error", "Please enter dates in the format YYYY-MM-DD."
            )
            return

        # Attempt to create the election
        if self.client(**election_details):
            messagebox.showinfo("Success", "The election was created successfully!")
        else:
            messagebox.showerror(
                "Error",
                f"Election with the name {election_details['election_name']} exists.",
            )

    def show(self):
        self.window.grab_set()


class ResultsViewer:
    def __init__(self, parent, client):
        self.client = client
        self.window = tk.Toplevel(parent)
        self.window.title("Election Results")
        self.window.geometry("1000x600")

        tk.Label(self.window, text="Please select one of the elections:").pack(pady=10)

        # Get election names for dropdown
        election_details = client(query_type="list_elections")
        self.election_details = election_details
        elections = [election["name"] for election in election_details]

        self.selected_election = tk.StringVar(self.window)
        self.selected_election.set(elections[0])

        tk.OptionMenu(self.window, self.selected_election, *elections).pack()
        tk.Button(self.window, text="View results", command=self.get_results).pack(
            pady=10
        )

        # Create a frame for election details
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
            label_value = tk.Label(self.details_frame, text="")
            label_value.grid(row=i, column=1, padx=5, sticky=tk.W)
            self.details_label_widgets[self.details_keys[i]] = label_value

        # Set up results table
        columns = ("Candidate", "Election", "Votes")
        self.tree = ttk.Treeview(self.window, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)

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
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def get_results(self):
        # Get results for the selected election
        selected_election_name = self.selected_election.get()
        results = self.client(
            query_type="view_results", election_name=selected_election_name
        )

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

        if selected_election_info:
            for key, label_widget in self.details_label_widgets.items():
                label_widget.config(text=selected_election_info.get(key, ""))

    def show(self):
        self.window.grab_set()


class VoteWindow:
    def __init__(self, parent, client):
        self.client = client
        self.window = tk.Toplevel(parent)
        self.window.title(f"Vote as {self.client.user_logged_in}")
        self.window.geometry("500x250")

        tk.Label(self.window, text="Please select an election").pack(pady=(30, 0))

        elections = [e["name"] for e in client(query_type="list_live_elections")]
        self.selected_election = tk.StringVar(self.window)
        self.selected_election.set(elections[0])
        tk.OptionMenu(
            self.window,
            self.selected_election,
            *elections,
            command=self.update_candidates,
        ).pack(pady=(10, 10))

        self.selected_candidate = tk.StringVar(self.window)
        self.candidate_menu = tk.OptionMenu(self.window, self.selected_candidate, "")
        self.candidate_menu.pack()

        tk.Button(self.window, text="Vote", command=self.submit_vote).pack(pady=20)

    def update_candidates(self, selected_election):
        candidates = [
            c["name"]
            for c in self.client(
                query_type="list_election_candidates", election_name=selected_election
            )
        ]
        self.selected_candidate.set(candidates[0] if candidates else "")
        self.candidate_menu["menu"].delete(0, "end")
        for candidate in candidates:
            self.candidate_menu["menu"].add_command(
                label=candidate, command=tk._setit(self.selected_candidate, candidate)
            )

    def submit_vote(self):
        election = self.selected_election.get()
        candidate = self.selected_candidate.get()

        if self.client(
            query_type="vote",
            username=self.client.user_logged_in,
            election_name=election,
            candidate_name=candidate,
        ):
            messagebox.showinfo(
                "Vote Successful", f"Successfully voted for {candidate} in {election}."
            )
            self.window.destroy()
        else:
            messagebox.showwarning(
                "Vote Failed", "You have already voted in this election."
            )

    def show(self):
        self.window.grab_set()


# Running the Election App
if __name__ == "__main__":
    app = ElectionApp()
    app.run()
