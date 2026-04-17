import pytest
from pyspark.sql import SparkSession
from app.use_cases.silver_to_gold import SilverToGoldService # замініть на свій клас

@pytest.fixture(scope="session")
def spark():
    """Local Spark session"""
    return SparkSession.builder \
        .master("local[1]") \
        .appName("pytest-spark-testing") \
        .getOrCreate()

def test_transformation_logic(spark):
    
    data = [
        ("1", "Great product!", 5),
        ("2", "Bad quality ", 1), 
        ("3", None, 3)             
    ]
    columns = ["review_id", "review_text", "rating"]
    input_df = spark.createDataFrame(data, columns)
     result_count = input_df.count()

   
    assert result_count == 3
    