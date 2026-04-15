import os
from pyspark.sql import SparkSession
from pyspark import SparkConf

class SparkManager:
    @staticmethod
    def get_session(app_name: str, config):
        # 1. Створюємо сесію з JAR-пакетами
        spark = SparkSession.builder \
            .appName(app_name) \
            .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
            .config("spark.driver.host", "127.0.0.1") \
            .getOrCreate()

        # 2. Жорстко прописуємо конфіг безпосередньо в Hadoop контекст сесії
        # Це гарантує, що Spark побачить ці налаштування
        hadoop_conf = spark._jsc.hadoopConfiguration()
        
        hadoop_conf.set("fs.s3a.endpoint", "http://minio:9000")
        hadoop_conf.set("fs.s3a.access.key", "minioadmin")
        hadoop_conf.set("fs.s3a.secret.key", "minioadmin")
        
        hadoop_conf.set("fs.s3a.path.style.access", "true")
        hadoop_conf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        hadoop_conf.set("fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
        
        # Тайм-аути
        hadoop_conf.set("fs.s3a.connection.timeout", "60000")
        hadoop_conf.set("fs.s3a.connection.establish.timeout", "60000")

        return spark