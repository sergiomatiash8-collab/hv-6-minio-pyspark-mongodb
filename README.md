HV-6: Amazon Reviews ETL Pipeline with PySpark, MinIO, and MongoDB
Project: Data Engineering ETL Pipeline
Date: April 2026
Status:  Complete

 Project Overview
This project demonstrates a complete Medallion Architecture ETL pipeline that:

Loads Amazon Reviews CSV data into Bronze Layer (local)
Transforms to Silver Layer as Parquet (MinIO S3-compatible storage)
Processes in Gold Layer with PySpark (aggregations in Docker)
Stores results in MongoDB for analytics

Key Features:

46,823 verified reviews processed
35K unique products aggregated
30K unique customers tracked
42K monthly trends captured


Architecture
(screenshot)

Project Structure
HV_6_Minio_PySpark_MongoDB/
├── data/
│   ├── bronze/
│   │   └── amazon_reviews.csv (483 MB - not in git)
│   ├── silver/
│   │   └── reviews.parquet (generated locally, not in git)
│   └── gold/
│
├── etl/
│   ├── transform/
│   │   └── bronze_to_silver.py    # CSV → Parquet → MinIO
│   └── load/
│       └── silver_to_gold.py      # Spark: Read MinIO → Aggregate → MongoDB
│
├── test/
│   └── (removed - using Docker Spark instead)
│
├── docker-compose.yml             # MinIO + MongoDB + Spark containers
├── .env                          # Credentials (MinIO, MongoDB)
├── .gitignore                    # Exclude data files
├── README.md                     # This file
└── venv/                         # Python virtual environment

Data Flow
Step 1: Bronze → Silver (Local Python)
python# etl/transform/bronze_to_silver.py
- Read: data/bronze/amazon_reviews.csv
- Select 6 columns: review_id, product_id, star_rating, 
                    review_date, customer_id, verified_purchase
- Convert to Parquet
- Upload to MinIO: s3://silver/reviews.parquet (10.8 MiB)
Step 2: Silver → Gold (Docker Spark)
python# etl/load/silver_to_gold.py
SparkConf Settings:
  - spark.hadoop.fs.s3a.endpoint: http://minio:9000
  - MongoDB: mongodb://admin:password@mongodb:27017

Data Processing:
  1. Read from: s3a://silver/reviews.parquet
  2. Remove NULLs in: review_id, product_id, star_rating, review_date
  3. Convert review_date to DateType
  4. Filter: verified_purchase = 1 (46,823 rows)

Aggregations (PySpark → MongoDB):
   products_agg (35K docs)
     - product_id
     - total_reviews (COUNT)
     - avg_rating (AVG(star_rating))

  customers_agg (30K docs)
     - customer_id
     - review_count (COUNT)

   monthly_agg (42K docs)
     - product_id
     - year
     - month
     - monthly_count (COUNT reviews per month)

 Getting Started
Prerequisites

Docker & Docker Compose
Python 3.13+ with venv
MongoDB Compass (optional, for visualization)
Amazon Reviews CSV dataset (483 MB)

Installation

Clone & Setup

bash   cd HV_6_Minio_PySpark_MongoDB
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt  # If exists, or install manually:
   pip install pandas minio pymongo python-dotenv pyspark

Download Dataset

Place amazon_reviews.csv in data/bronze/
File size: ~483 MB
Columns: 15 total (we use 6)


Start Docker Containers

bash   docker-compose up -d

MinIO: http://localhost:9000 (UI: http://localhost:9001)
MongoDB: localhost:27017
Spark: localhost:8888 (Jupyter)


Load Bronze → Silver (Local)

bash   python etl/transform/bronze_to_silver.py

Reads CSV locally
Converts to Parquet
Uploads to MinIO


Process Silver → Gold (Docker Spark)

bash   docker-compose exec spark spark-submit \
     --packages org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \
     /etl/load/silver_to_gold.py

Reads from MinIO (s3a://)
Processes with Spark in Docker
Writes to MongoDB collections


MongoDB Collections
1. products_agg (35K documents)
Query example:
javascriptdb.products_agg.findOne()
// Output:
{
  _id: ObjectId(...),
  product_id: "0842329129",
  total_reviews: 3,
  avg_rating: 1.0
}

// Use case: Get top products by review count
db.products_agg.find().sort({ total_reviews: -1 }).limit(10)
2. customers_agg (30K documents)
Query example:
javascriptdb.customers_agg.findOne()
// Output:
{
  _id: ObjectId(...),
  customer_id: 50030450,
  review_count: 1
}

// Use case: Find power reviewers
db.customers_agg.find().sort({ review_count: -1 }).limit(10)
3. monthly_agg (42K documents)
Query example:
javascriptdb.monthly_agg.findOne()
// Output:
{
  _id: ObjectId(...),
  product_id: "0486265250",
  year: 2005,
  month: 10,
  monthly_count: 1
}

// Use case: Trend analysis for a product
db.monthly_agg.find({ 
  product_id: "0486265250" 
}).sort({ year: 1, month: 1 })

Configuration
.env File
env# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_ENDPOINT=http://localhost:9000

# MongoDB
MONGO_ROOT_USER=admin
MONGO_ROOT_PASSWORD=password
MONGO_URI=mongodb://admin:password@localhost:27017
docker-compose.yml
Services:

MinIO: S3-compatible object storage
MongoDB: NoSQL database
Spark: PySpark with Jupyter notebook


Processing Statistics
MetricValueInput CSV Size483 MBInput Rows~10M (estimated)Cleaned Rows46,823  Null Removals~9,953,177Products35KCustomers30KDate Range2005-2014Processing Time~5 seconds (Docker Spark)

 Deliverables
1. PySpark Script (etl/load/silver_to_gold.py)

Ingestion from MinIO (S3A)
Data cleaning (NULL removal)
Type conversion (DateType)
3 aggregation queries
MongoDB storage

 2. Docker Setup (docker-compose.yml)

MinIO container for S3 storage
MongoDB container with auth
Spark container with PySpark
Internal Docker network

 3. Screenshots

MongoDB Compass: products_agg (35K docs)
MongoDB Compass: customers_agg (30K docs)
MongoDB Compass: monthly_agg (42K docs)


 Notes

Architecture: Medallion (Bronze → Silver → Gold)
Tools: PySpark, MinIO, MongoDB, Docker
Data Format: CSV → Parquet → MongoDB
Storage: Local (Bronze) → MinIO (Silver) → MongoDB (Gold)
Processing: Local Python + Docker Spark


 References

Apache Spark Documentation
MinIO S3 Compatibility
MongoDB Documentation
Medallion Architecture



Last Updated: April 5, 2026
Status: Complete & Tested