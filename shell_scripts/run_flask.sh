#!/bin/bash
# Set Environment variables
export FLASK_APP=app
export FLASK_ENV=development
export CUSTOMERS_DATABASE_URL=postgresql://customer_db_user:Gl00m15@blue-sky4all.duckdns.org/customer_service_db
export REDIS_HOST=blue-sky4all.duckdns.org
export REDIS_PORT=3600
export CUSTOMERS_BASE_URL=http://localhost:5000/api/v1/customers
export AUTH_BASE_URL=https://blue-sky4all.duckdns.org
export SECRET_KEY=hudTTPZbw6WV4yxEUnVdT5CooIT1TepeD0-Nwlw_-D4

# Running Flask server with --debug mode
/Users/macbook/PycharmProjects/flask-microserv-api-v1/venv/bin/python -m flask run --debug
