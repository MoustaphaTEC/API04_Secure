# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip3.8 install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=twilio_verify.py
ENV FLASK_ENV=development
ENV FLASK_DEBUG=True
ENV START_NGROK=1

# Run app.py when the container launches
CMD ["flask", "run", "--host=127.0.0.1"]