# Використовуємо Bullseye (там є Java 11)
FROM python:3.11-slim-bullseye

# Встановлюємо Java 11
RUN apt-get update && apt-get install -y openjdk-11-jre-headless && apt-get clean

# Решта файлу (WORKDIR, COPY, RUN pip...) залишається без змін
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONPATH=/app
CMD ["python", "main_bronze_to_silver.py"]