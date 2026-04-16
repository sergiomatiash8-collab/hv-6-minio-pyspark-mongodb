import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Завантажуємо .env
load_dotenv()

# 2. Визначаємо базову директорію проєкту
# Це шлях до папки HV_6_Minio_PySpark_MongoDB
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 3. ВИПРАВЛЕННЯ ДЛЯ WINDOWS (HADOOP/SPARK)
# Вказуємо Spark, де лежить наш "імітатор" Hadoop
hadoop_path = str(BASE_DIR / "hadoop")
os.environ["HADOOP_HOME"] = hadoop_path
os.environ["hadoop.home.dir"] = hadoop_path
# Додаємо шлях до winutils.exe у системний PATH
os.environ["PATH"] += os.pathsep + str(BASE_DIR / "hadoop" / "bin")

class Config:
    # MinIO settings
    # Якщо запускаєш локально (python...), використовуй localhost
    # Якщо всередині Docker, тут має бути назва сервісу (наприклад, minio)
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
    MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true"

    # Spark settings
    SPARK_APP_NAME = "AmazonReviewsETL"
    # Додаємо Spark Master (local[*] означає використовувати всі ядра процесора)
    SPARK_MASTER = "local[*]"
    
    # MongoDB settings
    MONGO_URL = os.getenv("MONGO_URL")

    @classmethod
    def validate(cls):
        """Перевірка, чи всі критичні змінні завантажені"""
        critical_vars = {
            "MINIO_ACCESS_KEY": cls.MINIO_ACCESS_KEY,
            "MINIO_SECRET_KEY": cls.MINIO_SECRET_KEY,
            "MONGO_URL": cls.MONGO_URL
        }
        missing = [k for k, v in critical_vars.items() if not v]
        if missing:
            print(f"⚠️ ПОПЕРЕДЖЕННЯ: Відсутні змінні в .env: {', '.join(missing)}")