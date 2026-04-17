import os
from pyspark.sql import SparkSession
from pyspark import SparkConf
import structlog
from app.core.exceptions import SparkSessionError

logger = structlog.get_logger()

class SparkManager:
    @staticmethod
    def get_session(app_name: str, config):
        """
        Create Spark session with S3A configuration.
        """
        try:
            logger.info("spark_session_init_start", app_name=app_name)

            conf = SparkConf()
            conf.setAll([
                ("spark.app.name", app_name),
                # Використовуємо перевірені версії для PySpark 3.4.1
                ("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262"),
                ("spark.driver.memory", "2g"),
                ("spark.executor.memory", "2g"),
                ("spark.sql.adaptive.enabled", "true"),
                
                # S3A / MinIO Налаштування
                ("spark.hadoop.fs.s3a.endpoint", f"http://{config.MINIO_ENDPOINT}"),
                ("spark.hadoop.fs.s3a.access.key", config.MINIO_ACCESS_KEY),
                ("spark.hadoop.fs.s3a.secret.key", config.MINIO_SECRET_KEY),
                ("spark.hadoop.fs.s3a.path.style.access", "true"),
                ("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem"),
                ("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider"),
                
                # КРИТИЧНІ ПАРАМЕТРИ ДЛЯ DOCKER
                ("spark.hadoop.fs.s3a.connection.ssl.enabled", "false"),
                ("spark.hadoop.fs.s3a.endpoint.region", "us-east-1"),
                
                # Таймаути та спроби
                ("spark.hadoop.fs.s3a.connection.establish.timeout", "10000"),
                ("spark.hadoop.fs.s3a.connection.timeout", "10000"),
                ("spark.hadoop.fs.s3a.attempts.maximum", "3")
            ])

            spark = SparkSession.builder.config(conf=conf).getOrCreate()

            # Валідація з'єднання
            SparkManager._validate_s3_connection(spark)

            logger.info("spark_session_init_success", 
                        app_name=app_name, 
                        spark_version=spark.version)
            return spark

        except Exception as e:
            logger.error("spark_session_init_failed", app_name=app_name, error=str(e))
            raise SparkSessionError(f"Failed to initialize Spark: {e}")

    @staticmethod
    def _validate_s3_connection(spark):
        """Test S3/MinIO connectivity before proceeding."""
        try:
            sc = spark.sparkContext
            # Перевіряємо шлях silver, який вже має існувати
            path = sc._gateway.jvm.org.apache.hadoop.fs.Path("s3a://silver/")
            fs = sc._gateway.jvm.org.apache.hadoop.fs.FileSystem.get(
                path.toUri(), 
                sc._jsc.hadoopConfiguration()
            )
            if not fs.exists(path):
                logger.warning("s3_path_not_found", path="s3a://silver/")
            else:
                logger.info("s3_connection_validated")
        except Exception as e:
            logger.error("s3_connection_validation_failed", error=str(e))
            raise SparkSessionError(f"MinIO not accessible: {e}")