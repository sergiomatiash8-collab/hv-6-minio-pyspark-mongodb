import os
import sys
from pyspark.sql import SparkSession


base_path = r"C:\Users\Admin\Desktop\HV_6_Minio_PySpark_MongoDB"
os.environ['HADOOP_HOME'] = os.path.join(base_path, "hadoop")
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable


os.environ['PATH'] = os.environ['HADOOP_HOME'] + "\\bin;" + os.environ['PATH']


from validators.data_validator import DataValidator

def main():
    
    spark = SparkSession.builder \
        .appName("FinalValidationTest") \
        .master("local[1]") \
        .getOrCreate()

    try:
        
        test_data = [
            ("101", "Correct Item", 100.0),
            (None, "Missing ID", 50.0),      
            ("103", "Negative Price", -10.0) 
        ]
        columns = ["id", "name", "price"]
        df = spark.createDataFrame(test_data, columns)

        print("\n=== Data begore cleaning ===")
        df.show()

        
        clean_df = DataValidator.validate_all(df)

        print("=== Data after validation ===")
        clean_df.show()

    except Exception as e:
        print(f"\n Error: {e}")
    finally:
        spark.stop()

if __name__ == "__main__":
    main()