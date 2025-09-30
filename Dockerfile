FROM python:3.12-alpine

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY locales/ ./locales/

# Expose webhook port
EXPOSE 8089

# Run the bot
CMD ["python", "-m", "src"]