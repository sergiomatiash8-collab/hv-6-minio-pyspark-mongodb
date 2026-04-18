import os
from app.core.config import Config
from app.infrastructure.minio_adapter import MinioAdapter
from app.use_cases.bronze_to_silver import BronzeToSilverService

def main():
    
    # Initialize MinIO adapter with configuration settings
    adapter = MinioAdapter(
        endpoint=Config.MINIO_ENDPOINT,
        access_key=Config.MINIO_ACCESS_KEY,
        secret_key=Config.MINIO_SECRET_KEY,
        secure=Config.MINIO_SECURE
    )

    # Initialize the processing service
    service = BronzeToSilverService(adapter)

    # Path to the local bronze data file
    local_file = "data/bronze/amazon_reviews.csv" 
    
    # Check if the source file exists before processing
    if not os.path.exists(local_file):
        print(f"Error: File not found at path {local_file}")
        print("Please verify if the terminal is running in the project root directory.")
        return

    try:
        print(f"Reading CSV file: {local_file}...")
        
        # Execute transformation and upload to MinIO
        service.execute(
            local_path=local_file,
            bucket_name="silver",
            object_name="amazon_reviews.parquet"
        )
        
        print("Success: Parquet file has been uploaded to MinIO (bucket 'silver').")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()