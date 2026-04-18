class DataValidator:
    @staticmethod
    def validate_all(df, is_spark=True):
        print(f"\n>>> STARTING VALIDATION (Spark Mode: {is_spark}) <<<")
        
        if is_spark:
            from pyspark.sql.functions import col, length
            
            # Define validation mask for Spark DataFrame
            valid_mask = (col("review_id").isNotNull()) & \
                         (col("rating") >= 1) & (col("rating") <= 5) & \
                         (length(col("review_body")) >= 5)
            
            clean_df = df.filter(valid_mask)
            rejected_df = df.filter(~valid_mask)
        else:
            
            # Define validation mask for Pandas DataFrame
            mask = (
                df['review_id'].notnull() & 
                df['review_body'].notnull() &
                (df['rating'] >= 1) & (df['rating'] <= 5) &
                (df['review_body'].str.len() >= 5)
            )
            
            clean_df = df[mask]
            rejected_df = df[~mask] 
        
        print(f"[INFO] Success: {len(clean_df)} rows.")
        print(f"[WARNING] Rejected (quarantined): {len(rejected_df)} rows.")
        
        return clean_df, rejected_df