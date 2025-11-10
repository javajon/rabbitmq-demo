FROM python:3.14-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY consumer.py .
RUN chmod +x consumer.py
CMD ["python", "consumer.py"]
