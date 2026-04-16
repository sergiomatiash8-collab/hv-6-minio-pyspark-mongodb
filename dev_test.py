import os
import sys
from pyspark.sql import SparkSession

# 1. Налаштовуємо шляхи (ми вже знаємо, що вони правильні)
base_path = r"C:\Users\Admin\Desktop\HV_6_Minio_PySpark_MongoDB"
os.environ['HADOOP_HOME'] = os.path.join(base_path, "hadoop")
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

# Додаємо bin до PATH, щоб Spark бачив winutils.exe
os.environ['PATH'] = os.environ['HADOOP_HOME'] + "\\bin;" + os.environ['PATH']

# Імпортуємо ваш валідатор (впевнимося, що папка validators поруч)
from validators.data_validator import DataValidator

def main():
    # 2. Ініціалізація Spark
    spark = SparkSession.builder \
        .appName("FinalValidationTest") \
        .master("local[1]") \
        .getOrCreate()

    try:
        # 3. Створюємо тестові дані (з помилками для перевірки)
        test_data = [
            ("101", "Correct Item", 100.0),
            (None, "Missing ID", 50.0),      # Має бути видалено
            ("103", "Negative Price", -10.0) # Має бути видалено
        ]
        columns = ["id", "name", "price"]
        df = spark.createDataFrame(test_data, columns)

        print("\n=== ДАНІ ДО ОЧИЩЕННЯ ===")
        df.show()

        # 4. Викликаємо наш валідатор
        clean_df = DataValidator.validate_all(df)

        print("=== ДАНІ ПІСЛЯ ВАЛІДАЦІЇ ===")
        clean_df.show()

    except Exception as e:
        print(f"\nСталася помилка: {e}")
    finally:
        spark.stop()

if __name__ == "__main__":
    main()