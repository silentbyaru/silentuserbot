FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080  # Lets Koyeb know we are exposing this port for FastAPI health check

CMD ["python3", "bot.py"]
