import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession

load_dotenv()

def get_spark_session():
    # Налаштування робочої директорії для Windows
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.environ["HADOOP_HOME"] = os.path.join(base_dir, "venv")
    
    return (SparkSession.builder
        .appName("AmazonReviewsETL")
        # Пакет hadoop-aws та критично важливий bundle зі всіма класами AWS SDK
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.6,com.amazonaws:aws-java-sdk-bundle:1.12.367")
        
        # Конфігурація MinIO (S3A)
        .config("spark.hadoop.fs.s3a.endpoint", os.getenv("MINIO_ENDPOINT"))
        .config("spark.hadoop.fs.s3a.access.key", os.getenv("MINIO_ROOT_USER"))
        .config("spark.hadoop.fs.s3a.secret.key", os.getenv("MINIO_ROOT_PASSWORD"))
        
        # ПАРАМЕТРИ ЧАСУ (Тільки цифри! Без "s", "ms" тощо)
        # 60000 = 60 секунд
        .config("spark.hadoop.fs.s3a.connection.timeout", "60000")
        .config("spark.hadoop.fs.s3a.connection.establish.timeout", "10000")
        
        # Авторизація: Simple каже "бери логін/пароль з конфігу вище і не шукай нічого в системі"
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
        
        # Додаткові налаштування для сумісності з MinIO
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")  # Якщо MinIO без SSL (http)
        
        # Локальні налаштування драйвера
        .config("spark.driver.host", "127.0.0.1")
        .getOrCreate())