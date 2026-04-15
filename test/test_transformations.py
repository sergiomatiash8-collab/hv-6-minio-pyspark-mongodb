import pytest
from pyspark.sql import SparkSession
from app.use_cases.silver_to_gold import SilverToGoldService # замініть на свій клас

@pytest.fixture(scope="session")
def spark():
    """Створюємо локальну сесію Spark для тестів"""
    return SparkSession.builder \
        .master("local[1]") \
        .appName("pytest-spark-testing") \
        .getOrCreate()

def test_transformation_logic(spark):
    # 1. Готуємо фейкові вхідні дані (Arrange)
    data = [
        ("1", "Great product!", 5),
        ("2", "Bad quality ", 1), # зайвий пробіл в кінці
        ("3", None, 3)             # пустий текст
    ]
    columns = ["review_id", "review_text", "rating"]
    input_df = spark.createDataFrame(data, columns)

    # 2. Викликаємо твою логіку (Act)
    # Припустимо, у тебе є функція clean_data
    # df_cleaned = clean_data(input_df) 
    
    # Для прикладу просто перевіримо count
    result_count = input_df.count()

    # 3. Перевіряємо результат (Assert)
    assert result_count == 3
    # assert df_cleaned.filter(df_cleaned.review_text.isNull()).count() == 0