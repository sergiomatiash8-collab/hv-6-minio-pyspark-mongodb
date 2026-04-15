from app.core.transformers import AmazonReviewTransformer

class BronzeToSilverService:
    def __init__(self, minio_adapter):
        self.minio_adapter = minio_adapter

    def execute(self, local_path: str, bucket_name: str, object_name: str):
        print(f"📦 Процес розпочато для: {local_path}")

        # 1. Читаємо вхідні дані
        with open(local_path, 'r', encoding='utf-8') as f:
            raw_data = f.read()

        # 2. Викликаємо бізнес-логіку (Core)
        # Тепер ми можемо легко змінити цей крок на інший трансформер
        parquet_data = AmazonReviewTransformer.transform_to_parquet(raw_data)

        # 3. Зберігаємо результат (Infrastructure)
        self.minio_adapter.upload_fileobj(
            bucket_name=bucket_name,
            object_name=object_name,
            data=parquet_data
        )
        
        print(f"✅ Результат збережено в {bucket_name}")