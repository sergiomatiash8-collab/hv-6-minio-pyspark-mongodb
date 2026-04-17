
FROM python:3.11-slim-bullseye


RUN apt-get update && apt-get install -y openjdk-11-jre-headless && apt-get clean


WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONPATH=/app
CMD ["python", "main_bronze_to_silver.py"]