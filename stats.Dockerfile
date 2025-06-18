FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy everything inside ./src/stats into /app/stats in the container
COPY ./src/stats /app/stats

# Set Python path so it can resolve 'stats' as a package
ENV PYTHONPATH=/app

# Install required packages
RUN pip install --no-cache-dir flask sqlalchemy psycopg2-binary pika

# Set Python to not buffer stdout/stderr
ENV PYTHONUNBUFFERED=1

# Run the app from inside /app/stats
CMD ["python", "stats/app.py"]
