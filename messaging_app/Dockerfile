# Use Python 3.10 base image
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1 \
    PIP_NO_CACHE_DIR=1 \

# Set working directory
RUN mkdir -p /app
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY . /messaging_app

# Expose port
EXPOSE 8000

# Set the entry point for the container
CMD ["python manage.py migrate && python manage.py runserver 0.0.0:8000"]

