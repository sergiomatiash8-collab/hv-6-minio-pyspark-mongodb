from app.core.transformers import AmazonReviewTransformer

class BronzeToSilverService:
    def __init__(self, minio_adapter):
        self.minio_adapter = minio_adapter

    def execute(self, local_path: str, bucket_name: str, object_name: str):
        print(f"Process started: {local_path}")

        
        with open(local_path, 'r', encoding='utf-8') as f:
            raw_data = f.read()

        
        parquet_data = AmazonReviewTransformer.transform_to_parquet(raw_data)

        
        self.minio_adapter.upload_fileobj(
            bucket_name=bucket_name,
            object_name=object_name,
            data=parquet_data
        )
        
        print(f"Result in {bucket_name}")