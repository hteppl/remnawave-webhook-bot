FROM python:3.14-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk add --no-cache tzdata


COPY pyproject.toml ./
COPY src/ ./src/
COPY locales/ ./locales/

RUN pip install --no-cache-dir .

RUN adduser -D -H -u 10001 app && chown -R app:app /app
USER app

CMD ["python", "-m", "src"]
