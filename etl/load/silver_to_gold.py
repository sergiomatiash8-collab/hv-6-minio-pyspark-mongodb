import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, year, month, to_date
from pymongo import MongoClient
from minio import Minio
import io

load_dotenv()

# 1. Download Parquet з MinIO
minio_client = Minio("localhost:9000", access_key="minioadmin", secret_key="minioadmin", secure=False)
response = minio_client.get_object("silver", "reviews.parquet")
parquet_data = response.read()

# 2. Збережи локально
with open("data/silver/reviews.parquet", "wb") as f:
    f.write(parquet_data)

# 3. Spark Session
spark = SparkSession.builder.appName("SilverToGold").getOrCreate()

# 4. Читаємо Parquet
df = spark.read.parquet("data/silver/reviews.parquet")

# 5. Очистка
df_clean = df.filter(
    (col("review_id").isNotNull()) &
    (col("product_id").isNotNull()) &
    (col("star_rating").isNotNull()) &
    (col("review_date").isNotNull())
)

# 6. Convert to DateType
df_clean = df_clean.withColumn("review_date", to_date(col("review_date")))
df_clean = df_clean.withColumn("star_rating", col("star_rating").cast("float"))

# 7. Filter verified
df_verified = df_clean.filter(col("verified_purchase") == 1)

print(f"✅ Очищено: {df_verified.count()} рядків")

# 8. Aggregations
products_agg = df_verified.groupBy("product_id").agg(
    count("review_id").alias("total_reviews"),
    avg("star_rating").alias("avg_rating")
)

customers_agg = df_verified.groupBy("customer_id").agg(
    count("review_id").alias("review_count")
)

monthly_agg = df_verified.withColumn("year", year("review_date")).withColumn("month", month("review_date")).groupBy("product_id", "year", "month").agg(
    count("review_id").alias("monthly_count")
)

# 9. MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client['amazon']

db.products_agg.delete_many({})
db.products_agg.insert_many(products_agg.toPandas().to_dict('records'))

db.customers_agg.delete_many({})
db.customers_agg.insert_many(customers_agg.toPandas().to_dict('records'))

db.monthly_agg.delete_many({})
db.monthly_agg.insert_many(monthly_agg.toPandas().to_dict('records'))

print("✅ Завантажено в MongoDB!")
spark.stop()