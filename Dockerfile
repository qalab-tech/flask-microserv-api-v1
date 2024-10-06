
FROM python:3.11-slim

# WORKDIR setup
WORKDIR /app

# Copy requirements.txt and install the dependences
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# COPY other files to Docker container
COPY . .

# Expose port 5000 for our microservice application
EXPOSE 5000

# Running our Flask app with Gunicorn (Production Mode)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]



