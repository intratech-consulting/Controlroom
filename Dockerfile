# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir pika

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME HeartbeatPublisher

# Run heartbeat_publisher.py when the container launches
CMD ["python", "./heartbeat_publisher.py"]
