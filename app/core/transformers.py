import pandas as pd
import io

class AmazonReviewTransformer:
    @staticmethod
    def transform_to_parquet(csv_content: str) -> io.BytesIO:
        """Clean transform: CSV -> Parquet Buffer"""
        cols = ['review_id', 'product_id', 'star_rating', 
                'review_date', 'verified_purchase', 'customer_id']
        
        
        df = pd.read_csv(io.StringIO(csv_content), sep=None, 
                         engine='python', usecols=cols, on_bad_lines='skip')
        
        parquet_buffer = io.BytesIO()
        df.to_parquet(parquet_buffer, index=False)
        parquet_buffer.seek(0)
        return parquet_buffer