FROM python:3.12-alpine

WORKDIR /app

# Copy and install dependencies (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project metadata
COPY pyproject.toml .

# Copy application code
COPY src/ ./src/
COPY locales/ ./locales/

# Run the bot
CMD ["python", "-m", "src"]