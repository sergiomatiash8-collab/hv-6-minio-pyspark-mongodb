from pyspark import SparkConf
from pyspark.sql import SparkSession
import os
from dotenv import load_dotenv

load_dotenv()

# Створюємо конфіг окремо
conf = SparkConf()
conf.setAppName("TestMinio")
# ПАКЕТИ
conf.set("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.6,com.amazonaws:aws-java-sdk-bundle:1.12.367")

# ПРИМУСОВО ЧИСЛА (БЕЗ 's')
conf.set("spark.hadoop.fs.s3a.connection.timeout", "60000")
conf.set("spark.hadoop.fs.s3a.connection.establish.timeout", "10000")

# ІНШІ НАЛАШТУВАННЯ
conf.set("spark.hadoop.fs.s3a.endpoint", os.getenv("MINIO_ENDPOINT"))
conf.set("spark.hadoop.fs.s3a.access.key", os.getenv("MINIO_ROOT_USER"))
conf.set("spark.hadoop.fs.s3a.secret.key", os.getenv("MINIO_ROOT_PASSWORD"))
conf.set("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
conf.set("spark.hadoop.fs.s3a.path.style.access", "true")
conf.set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
conf.set("spark.driver.host", "127.0.0.1")

spark = SparkSession.builder.config(conf=conf).getOrCreate()

try:
    print("--- СПРОБА ЧИТАННЯ ---")
    df = spark.read.parquet("s3a://silver/reviews.parquet")
    df.show(5)
except Exception as e:
    print(f"--- ПОМИЛКА: ---\n{e}")
finally:
    spark.stop()