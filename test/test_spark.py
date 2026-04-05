import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark import SparkConf

# 1️⃣ Windows HADOOP setup
os.environ['HADOOP_HOME'] = r'C:\Users\Admin\Desktop\HV_6_Minio_PySpark_MongoDB\hadoop'
os.environ['PATH'] = os.path.join(os.environ['HADOOP_HOME'], 'bin') + ';' + os.environ['PATH']

# 2️⃣ Load .env
load_dotenv()
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://127.0.0.1:9000")
MINIO_USER = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")

# 3️⃣ Set JVM args to fix "60s" error
os.environ['PYSPARK_SUBMIT_ARGS'] = (
    '--conf spark.hadoop.fs.s3a.connection.timeout=60000 '
    '--conf spark.hadoop.fs.s3a.connection.establish.timeout=5000 '
    '--conf spark.hadoop.fs.s3a.path.style.access=true '
    '--conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem '
    '--conf spark.hadoop.fs.s3a.aws.credentials.provider=org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider '
    'pyspark-shell'
)

# 4️⃣ Spark config
conf = SparkConf()
conf.setAppName("TestMinIO")
conf.set("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.530")

conf.set("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT)
conf.set("spark.hadoop.fs.s3a.access.key", MINIO_USER)
conf.set("spark.hadoop.fs.s3a.secret.key", MINIO_PASSWORD)
conf.set("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
conf.set("spark.driver.host", "127.0.0.1")
conf.set("spark.sql.shuffle.partitions", "8")

# 5️⃣ Create Spark session
spark = SparkSession.builder.config(conf=conf).getOrCreate()

# 6️⃣ Read Parquet from MinIO
try:
    print("Reading from MinIO...")
    df = spark.read.parquet("s3a://silver/reviews.parquet")
    df.show(5)
    print("SUCCESS! ✅")
except Exception as e:
    import traceback
    print("FAILED ❌")
    traceback.print_exc()
finally:
    spark.stop()