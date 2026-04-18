"""
End-to-end integration tests using testcontainers. 
Tests the full pipeline: Bronze -> Silver -> Gold -> MongoDB
"""

import pytest
import pandas as pd
import io
from testcontainers.minio import MinioContainer
from testcontainers.mongodb import MongoDbContainer
from pyspark.sql import SparkSession
from pymongo import MongoClient

from app.infrastructure.minio_adapter import MinioAdapter
from app.infrastructure.mongodb_adapter import MongoDBAdapter
from app.use_cases.silver_to_gold import SilverToGoldService

@pytest.fixture(scope="session")
def minio_container():
    """Start MinIO container for testing."""
    with MinioContainer(image="minio/minio:latest") as minio:
        yield minio

@pytest.fixture(scope="session")
def mongodb_container():
    """Start MongoDB container for testing."""
    with MongoDbContainer("mongo:7.0") as mongodb:
        yield mongodb

@pytest.fixture(scope="session")
def spark_session(minio_container):
    """Create Spark session configured for test MinIO."""
    endpoint = f"{minio_container.get_container_host_ip()}:{minio_container.get_exposed_port(9000)}"
    
    spark = SparkSession.builder \
        .appName("integration-test") \
        .master("local[2]") \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
        .config("spark.hadoop.fs.s3a.endpoint", f"http://{endpoint}") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
        .getOrCreate()
    
    yield spark
    spark.stop()

def test_full_pipeline(spark_session, minio_container, mongodb_container):
    """Test complete Bronze -> Silver -> Gold pipeline."""
    
    
    endpoint = f"{minio_container.get_container_host_ip()}:{minio_container.get_exposed_port(9000)}"
    minio_adapter = MinioAdapter(
        endpoint=endpoint,
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    
    
    for bucket in ["silver", "gold"]:
        if not minio_adapter.client.bucket_exists(bucket):
            minio_adapter.client.make_bucket(bucket)

    
    test_data = pd.DataFrame({
        'review_id': ['R1', 'R2', 'R3'],
        'product_id': ['P1', 'P1', 'P2'],
        'star_rating': [5, 4, 3],
        'review_date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'verified_purchase': [True, True, False],
        'customer_id': ['C1', 'C2', 'C3']
    })

    
    parquet_buffer = io.BytesIO()
    test_data.to_parquet(parquet_buffer, index=False)
    parquet_buffer.seek(0)

    minio_adapter.upload_fileobj(
        bucket_name="silver",
        object_name="test_reviews.parquet",
        data=parquet_buffer
    )

    
    mongodb_adapter = MongoDBAdapter(
        connection_string=mongodb_container.get_connection_url(),
        database="test_db"
    )

    service = SilverToGoldService(spark_session, mongodb_adapter)
    df_gold = service.execute(
        input_path="s3a://silver/test_reviews.parquet",
        output_path="s3a://gold/test_product_reviews.parquet"
    )

    
    assert df_gold.count() == 2  # P1 та P2
    
    p1_results = df_gold.filter(F.col("product_id") == "P1").collect()[0]
    assert p1_results["total_reviews"] == 2
    assert float(p1_results["avg_rating"]) == 4.5

    
    client = MongoClient(mongodb_container.get_connection_url())
    db = client['test_db']
    mongo_results = list(db['product_reviews_gold'].find())

    assert len(mongo_results) == 2
    assert any(r['product_id'] == 'P1' for r in mongo_results)
    
    mongodb_adapter.close()
    client.close()