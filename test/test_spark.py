import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark import SparkConf

# Set Hadoop home for Windows
os.environ['HADOOP_HOME'] = 'C:\\Users\\Admin\\Desktop\\HV_6_Minio_PySpark_MongoDB\\hadoop'
os.environ['PATH'] = 'C:\\Users\\Admin\\Desktop\\HV_6_Minio_PySpark_MongoDB\\hadoop\\bin;' + os.environ['PATH']

# Load environment variables
load_dotenv()

# Create Spark config
conf = SparkConf()
conf.setAppName("BronzeToSilver")

# Hadoop AWS packages
conf.set("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.261")

# Connection timeouts (milliseconds)
conf.set("spark.hadoop.fs.s3a.connection.timeout", "60000")
conf.set("spark.hadoop.fs.s3a.socket.send.buffer", "65536")
conf.set("spark.hadoop.fs.s3a.socket.recv.buffer", "65536")

# MinIO credentials
conf.set("spark.hadoop.fs.s3a.endpoint", os.getenv("MINIO_ENDPOINT"))
conf.set("spark.hadoop.fs.s3a.access.key", os.getenv("MINIO_ROOT_USER"))
conf.set("spark.hadoop.fs.s3a.secret.key", os.getenv("MINIO_ROOT_PASSWORD"))

# S3A configuration
conf.set("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
conf.set("spark.hadoop.fs.s3a.path.style.access", "true")
conf.set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
conf.set("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
conf.set("spark.driver.host", "127.0.0.1")
conf.set("spark.sql.warehouse.dir", "./spark-warehouse")

# Create Spark session
spark = SparkSession.builder.config(conf=conf).getOrCreate()

try:
    print("\n--- [START] Reading from MinIO ---")
    df = spark.read.parquet("s3a://silver/reviews.parquet")
    df.show(5)
    print("--- [SUCCESS] IT WORKS! ---")
except Exception as e:
    print(f"\n--- [FAILED] Error: ---\n{e}")
finally:
    spark.stop()