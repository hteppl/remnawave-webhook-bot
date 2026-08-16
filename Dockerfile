FROM python:3.14-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk add --no-cache tzdata

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml .

COPY src/ ./src/
COPY locales/ ./locales/

CMD ["python", "-m", "src"]
