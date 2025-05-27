FROM python:3.13-alpine

# Env to avoid writing .pyc files and output to stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /code

# Copy requirements file
COPY backend/requirements.txt .

# Install system dependencies and Python packages
RUN apk add --no-cache gcc musl-dev libffi-dev \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

# Don't copy code in dev - mounted via volume
# COPY backend .

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--reload"]
