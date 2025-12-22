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

# Command to run the application
# We use a shell to expand $PORT correctly at runtime
CMD sh -c "gunicorn crystals_project.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3"
