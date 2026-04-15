from pyspark.sql import SparkSession
from pyspark import SparkConf

class SparkManager:
    @staticmethod
    def get_session(app_name: str, config):
        """Створює та налаштовує SparkSession для роботи з S3A (MinIO)"""
        conf = SparkConf()
        conf.setAppName(app_name)
        
        # Налаштування пакетів для S3A
        conf.set("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262")

        # Налаштування підключення до MinIO
        conf.set("spark.hadoop.fs.s3a.endpoint", f"http://{config.MINIO_ENDPOINT}")
        conf.set("spark.hadoop.fs.s3a.access_key", config.MINIO_ACCESS_KEY)
        conf.set("spark.hadoop.fs.s3a.secret.key", config.MINIO_SECRET_KEY)
        conf.set("spark.hadoop.fs.s3a.path.style.access", "true")
        conf.set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        conf.set("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")

        return SparkSession.builder.config(conf=conf).getOrCreate()