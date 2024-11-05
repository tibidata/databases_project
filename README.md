# 💾 DATABASES_PROJECT

This project includes a MySQL-backed application with a Tkinter GUI front-end and a Flask API backend. The MySQL database, Flask API, and data storage are managed using Docker and Docker Compose, allowing seamless interaction between the desktop interface and database via the REST API.

## 🗺️ Project Structure

- **db_init**: Contains SQL scripts to initialize the MySQL database.
  - `init.sql`: SQL script that sets up the initial database schema and seed data.
  
- **notebooks**: Directory for Jupyter notebooks (if any are used for database exploration or testing).

- **src**: Core Python modules, including the Tkinter GUI application.
  - `tools`: Helper functions and modules for database operations.
    - `__init__.py`: Initialization file for the `tools` package.
    - `db_client.py`: Handles database connections and operations.
    - `query.py`: Defines and manages database queries.
    - `app.py`: Tkinter-based desktop GUI for interacting with the database through the Flask API.

- **webapp**: Contains the Flask backend API that connects to the MySQL database.
  - `app.py`: Flask application that serves as the backend, providing REST API endpoints for the Tkinter frontend.
  - `Dockerfile`: Dockerfile for building the Flask application container.
  - `requirements.txt`: Python dependencies for the Flask application.

- **docker-compose.yml**: Docker Compose configuration file to orchestrate the MySQL and Flask containers.

- **LICENSE**: License for the project.
- **README.md**: Project documentation.
- **requirements.txt**: Main dependencies for the core database-related modules.

## 🧑‍💻 Prerequisites

Ensure you have the following installed:

- **Docker**: To containerize and run the MySQL and Flask services.
- **Docker Compose**: To manage multi-container applications.
- **Python 3.8+**: For running the Tkinter application locally.
- **pip**: Python package manager, to install dependencies.

## 📦 Docker Compose Configuration

### `docker-compose.yml` Overview

The `docker-compose.yml` file configures two services:

- **db**: Runs a MySQL database container.
  - Uses the `mysql:latest` image.
  - Exposes MySQL on port `3307` (mapped from MySQL’s default port `3306`).
  - Loads the initial schema from `db_init/init.sql`.
  - Persists data in the `mysql_data` Docker volume.

- **web**: Runs the Flask backend API.
  - Builds the application from the `webapp` directory.
  - Exposes Flask on port `8080` (mapped from Flask’s default port `5000`).
  - Uses environment variables to connect to the MySQL database.
  - Depends on `db`, ensuring that the database starts first.

## 📜 Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/tibidata/databases_project
   cd databases_project
   ```

2. **Create a Virtual Environment**:

    It is always useful to create a virtual environment to install packages.

   ```bash
   python -m venv ./venv
   source ./venv/bin/activate
   ```    

3. **Install requirements for GUI**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Stop All docker-compose containers and remove volumes**

   ```bash
   docker-compose down -v
   ```    
5. **Set up docker containers with docker-compose**:

   ```bash
   docker-compose up --build
   ```    

6. **Run the application with GUI**:
   ```bash
   python ./src/app.py
   ```    

## 📖 License
This project is licensed under the terms specified in the LICENSE file.
