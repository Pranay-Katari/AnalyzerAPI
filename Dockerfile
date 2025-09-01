FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

CMD exec gunicorn --bind :$PORT --workers 2 --threads 8 --timeout 0 main:app
