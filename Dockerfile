FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer-cache friendly)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source and data
COPY src/ ./src/
COPY data/ ./data/

# Code Engine routes traffic to 8080 by default
ENV PORT=8080
EXPOSE 8080

CMD ["python", "src/app.py"]
