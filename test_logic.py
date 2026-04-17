import pandas as pd
from validators.data_validator import DataValidator


data = {
    "review_id": ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10"],
    "product_id": ["B01", "B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B09"],
    "rating": [5, 4, -1, 3, 5, 2, 10, 4, 5, 3], 
    "review_body": [
        "Great product, highly recommend!", 
        "Bad",                              
        "Average quality",                  
        "I love this thing so much",        
        "Super!",                           
        "Worst experience ever",            
        "The best!",                        
        "OK",                               
        "Just perfect and fast delivery",   
        "Neutral"                           
    ]
}
df = pd.DataFrame(data)


clean_df, rejected_df = DataValidator.validate_all(df, is_spark=False)

print("\n--- ✅ ЧИСТІ ДАНІ (Йдуть в базу) ---")
print(clean_df[['review_id', 'rating', 'review_body']])

print("\n--- ❌ КАРАНТИН (Сміття для звіту) ---")
print(rejected_df[['review_id', 'rating', 'review_body']])