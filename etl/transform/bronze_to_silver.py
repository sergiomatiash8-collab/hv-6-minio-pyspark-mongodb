import pandas as pd
from minio import Minio
import io
from dotenv import load_dotenv
import os

load_dotenv()

# 1. Читаємо тільки потрібні колонки (економимо пам'ять)
cols = ['review_id', 'product_id', 'star_rating', 'review_date', 'verified_purchase', 'customer_id']
# Читаємо файл, дозволяючи Pandas самому знайти розділювач
df = pd.read_csv('data/bronze/amazon_reviews.csv', sep=None, engine='python', usecols=cols, on_bad_lines='skip')

# 2. Конвертуємо в Parquet (в пам'яті)
parquet_buffer = io.BytesIO()
df.to_parquet(parquet_buffer, index=False)
parquet_buffer.seek(0)

# 3. Завантажуємо в MinIO
client = Minio("localhost:9000", access_key="minioadmin", secret_key="minioadmin", secure=False)

# Створюємо бакет, якщо його немає
if not client.bucket_exists("silver"):
    client.make_bucket("silver")

client.put_object("silver", "reviews.parquet", parquet_buffer, len(parquet_buffer.getvalue()))
print("✅ Файл успішно конвертовано та завантажено в MinIO (Silver Layer)!")