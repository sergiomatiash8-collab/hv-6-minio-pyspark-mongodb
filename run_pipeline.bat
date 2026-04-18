@echo off
setlocal
echo ==================================================
echo   AMAZON REVIEWS PIPELINE: STEP-BY-STEP
echo ==================================================

:: 1. INFRASTRUCTURE SETUP
echo [1/4] Starting Infrastructure...
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

echo Waiting for services to start (20s)...
timeout /t 20 /nobreak > NUL

:: 2. STEP 1: BRONZE TO SILVER (Populating MinIO)
echo [2/4] Step 1: Loading data into MinIO (Silver)...
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml run --rm app python main_bronze_to_silver.py

:: 3. STEP 2: SILVER TO GOLD (Analytics in MongoDB)
echo [3/4] Step 2: Processing data to MongoDB (Gold)...
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml run --rm app python main_silver_to_gold.py

echo ==================================================
echo   SUCCESS: Pipeline completed!
echo ==================================================
pause