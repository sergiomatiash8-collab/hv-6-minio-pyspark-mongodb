import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Set up Hadoop environment variables
hadoop_path = str(BASE_DIR / "hadoop")
os.environ["HADOOP_HOME"] = hadoop_path
os.environ["hadoop.home.dir"] = hadoop_path

# Add Hadoop bin directory to the system PATH
os.environ["PATH"] += os.pathsep + str(BASE_DIR / "hadoop" / "bin")

class Config:
    
    # MinIO configuration
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
    MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true"

    # Spark configuration
    SPARK_APP_NAME = "AmazonReviewsETL"
    SPARK_MASTER = "local[*]"
    
    # MongoDB configuration
    MONGO_URL = os.getenv("MONGO_URL")

    @classmethod
    def validate(cls):
        """Check if all critical environment variables are loaded"""
        critical_vars = {
            "MINIO_ACCESS_KEY": cls.MINIO_ACCESS_KEY,
            "MINIO_SECRET_KEY": cls.MINIO_SECRET_KEY,
            "MONGO_URL": cls.MONGO_URL
        }
        missing = [k for k, v in critical_vars.items() if not v]
        if missing:
            print(f" WARNING: Missing environment variables in .env: {', '.join(missing)}")