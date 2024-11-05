# Use the official Python image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the application code and requirements
COPY requirements.txt requirements.txt
COPY app.py app.py
COPY ./tools ./tools

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that the app will run on
EXPOSE 5000

# Define the command to run the application
CMD ["python", "app.py"]