# # Use Python 3.10 base image
# FROM python:3.10-slim

# ENV PYTHONDONTWRITEBYTECODE 1 \
#     PYTHONUNBUFFERED 1 \
#     PIP_NO_CACHE_DIR=1 \

# # Set working directory
# RUN mkdir -p /app
# WORKDIR /app

# # Install dependencies
# COPY requirements.txt .
# RUN pip install --upgrade pip && \
#     pip install -r requirements.txt

# # Copy application code
# COPY . /messaging_app

# # Expose port
# EXPOSE 8000

# # Set the entry point for the container
# CMD ["python manage.py migrate && python manage.py runserver 0.0.0:8000"]

# messaging_app/Dockerfile

# Use Python 3.10 base image
FROM python:3.10-slim

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Working directory
WORKDIR /app

# --- OS deps for mysqlclient (MySQL) ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmariadb-dev \
    pkg-config \
  && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (leverage layer caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copy application code
COPY . /app

# Expose Django dev server port
EXPOSE 8000

# Run migrations then start server (note: must use sh -c)
CMD sh -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"
