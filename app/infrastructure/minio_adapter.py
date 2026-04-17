from minio import Minio
import io

class MinioAdapter:
    def __init__(self, endpoint: str, access_key: str, secret_key: str, secure: bool):
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

    def upload_fileobj(self, bucket_name: str, object_name: str, data: io.BytesIO):
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)
        
        # Отримуємо розмір контенту перед завантаженням
        content_size = len(data.getbuffer()) 
        data.seek(0)
        
        res = self.client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=data,
            length=content_size, # Вказуємо точний розмір
            content_type='application/octet-stream'
        )
        return res