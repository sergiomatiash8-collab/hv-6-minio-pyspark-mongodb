import os
from pyspark.sql import SparkSession

class SparkManager:
    @staticmethod
    def get_session(app_name: str, config):
        # Визначаємо шлях до MinIO залежно від оточення
        # У Docker це буде http://minio:9000
        s3_endpoint = f"http://{config.MINIO_ENDPOINT}" 

        spark = SparkSession.builder \
            .appName(app_name) \
            .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
            .getOrCreate()

        hadoop_conf = spark._jsc.hadoopConfiguration()
        
        # Використовуємо значення з нашого Config об'єкта
        hadoop_conf.set("fs.s3a.endpoint", s3_endpoint)
        hadoop_conf.set("fs.s3a.access.key", config.MINIO_ACCESS_KEY)
        hadoop_conf.set("fs.s3a.secret.key", config.MINIO_SECRET_KEY)
        
        hadoop_conf.set("fs.s3a.path.style.access", "true")
        hadoop_conf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        hadoop_conf.set("fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
        
        # Суворо числові значення для уникнення помилки "60s"
        hadoop_conf.set("fs.s3a.connection.timeout", "60000")
        hadoop_conf.set("fs.s3a.connection.establish.timeout", "60000")

        return spark