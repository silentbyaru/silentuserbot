FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080  # Let Koyeb know this is the health check port

CMD ["python3", "bot.py"]
