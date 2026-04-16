import os
from pyspark.sql import SparkSession
from pyspark import SparkConf

class SparkManager:
    @staticmethod
    def get_session(app_name: str, config):
        conf = SparkConf()
        
        # 1. Пакет драйверів
        conf.set("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262")
        
        # 2. Налаштування S3A (Докер-версія)
        # Важливо: використовуємо префікс spark.hadoop.
        conf.set("spark.hadoop.fs.s3a.endpoint", f"http://{config.MINIO_ENDPOINT}")
        conf.set("spark.hadoop.fs.s3a.access.key", config.MINIO_ACCESS_KEY)
        conf.set("spark.hadoop.fs.s3a.secret.key", config.MINIO_SECRET_KEY)
        
        conf.set("spark.hadoop.fs.s3a.path.style.access", "true")
        conf.set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        conf.set("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
        
        # Виправляємо проблему з таймаутами (тільки цифри)
        conf.set("spark.hadoop.fs.s3a.connection.timeout", "60000")
        
        # 3. Створюємо сесію
        spark = SparkSession.builder \
            .appName(app_name) \
            .config(conf=conf) \
            .getOrCreate()

        return spark