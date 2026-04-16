import pytest
from pyspark.sql import SparkSession

@pytest.fixture(scope="session")
def spark():
    # Створюємо локальну Spark-сесію для тестів
    return SparkSession.builder \
        .master("local[1]") \
        .appName("testing") \
        .getOrCreate()

def test_simple_count(spark):
    # Створюємо простий DataFrame з двох рядків
    df = spark.createDataFrame([("Alice", 1), ("Bob", 2)], ["name", "id"])
    
    # Перевіряємо, чи кількість рядків дорівнює 2
    assert df.count() == 2