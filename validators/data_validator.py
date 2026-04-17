class DataValidator:
    @staticmethod
    def validate_all(df, is_spark=True):
        print(f"\n>>> ЗАПУСК ВАЛІДАЦІЇ (Режим Spark: {is_spark}) <<<")
        
        if is_spark:
            from pyspark.sql.functions import col, length
            
            valid_mask = (col("review_id").isNotNull()) & \
                         (col("rating") >= 1) & (col("rating") <= 5) & \
                         (length(col("review_body")) >= 5)
            
            clean_df = df.filter(valid_mask)
            rejected_df = df.filter(~valid_mask)
        else:
            
            mask = (
                df['review_id'].notnull() & 
                df['review_body'].notnull() &
                (df['rating'] >= 1) & (df['rating'] <= 5) &
                (df['review_body'].str.len() >= 5)
            )
            
            clean_df = df[mask]
            rejected_df = df[~mask] 
        
        print(f"[INFO] Успішно: {len(clean_df)} рядків.")
        print(f"[WARNING] Відхилено (в карантин): {len(rejected_df)} рядків.")
        
        return clean_df, rejected_df