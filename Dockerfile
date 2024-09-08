# Use the official Python image as the base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Command to run the Streamlit app, updated to point to the refactored main.py
CMD ["sh", "-c", "streamlit run app/main.py --server.port=${PORT} --server.enableCORS=false"]