import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, year, month, to_date
from pyspark import SparkConf
from pymongo import MongoClient

load_dotenv()

# 1. Spark Config з S3A
conf = SparkConf()
conf.setAppName("SilverToGold")
conf.set("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262")

# MinIO credentials
conf.set("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")
conf.set("spark.hadoop.fs.s3a.access.key", "minioadmin")
conf.set("spark.hadoop.fs.s3a.secret.key", "minioadmin")
conf.set("spark.hadoop.fs.s3a.path.style.access", "true")
conf.set("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
conf.set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

# 2. Spark Session
spark = SparkSession.builder.config(conf=conf).getOrCreate()

# 3. Читаємо Parquet прямо з MinIO
df = spark.read.parquet("s3a://silver/reviews.parquet")

# 4. Очистка
df_clean = df.filter(
    (col("review_id").isNotNull()) &
    (col("product_id").isNotNull()) &
    (col("star_rating").isNotNull()) &
    (col("review_date").isNotNull())
)

# 5. Convert to DateType
df_clean = df_clean.withColumn("review_date", to_date(col("review_date")))
df_clean = df_clean.withColumn("star_rating", col("star_rating").cast("float"))

# 6. Filter verified
df_verified = df_clean.filter(col("verified_purchase") == 1)

print(f"✅ Очищено: {df_verified.count()} рядків")

# 7. Aggregations
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

# 8. MongoDB
client = MongoClient("mongodb://admin:password@mongodb:27017")
db = client['amazon']

db.products_agg.delete_many({})
db.products_agg.insert_many(products_agg.toPandas().to_dict('records'))

db.customers_agg.delete_many({})
db.customers_agg.insert_many(customers_agg.toPandas().to_dict('records'))

db.monthly_agg.delete_many({})
db.monthly_agg.insert_many(monthly_agg.toPandas().to_dict('records'))

print("✅ Завантажено в MongoDB!")
spark.stop()