# Start from the official Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the Python source code from 'src' into the container's /app directory
COPY ./src .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using uvicorn
# We use --host 0.0.0.0 to make it accessible outside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]