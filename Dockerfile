FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY src/ ./src/
COPY data/ ./data/

# Expose all ports
EXPOSE 8010 8011 8501

CMD ["python", "-m", "src.main"]