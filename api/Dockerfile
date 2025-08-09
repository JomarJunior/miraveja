FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install the dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Install TKinter
RUN apt-get update && \
    apt-get install -y python3-tk tk-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the rest of the application code into the container
COPY . .

# Define the command to run the application
CMD ["python", "main.py"]