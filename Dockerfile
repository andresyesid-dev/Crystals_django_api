FROM python:3.9-slim

WORKDIR /app

# Install system dependencies (needed for psycopg2 compilation sometimes, though binary is used)
# RUN apt-get update && apt-get install -y libpq-dev gcc

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

# PYTHONUNBUFFERED: forces Python to flush stdout/stderr immediately so logs
# from Django (running inside gunicorn workers) appear in Railway in real time.
ENV PYTHONUNBUFFERED=1

# Command to run the application
# Runs pending migrations then starts gunicorn
# --access-logfile - : sends gunicorn's per-request log to stdout (Railway captures it)
CMD sh -c "python manage.py migrate --no-input && gunicorn crystals_project.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --access-logfile -"
