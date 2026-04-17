@echo off
setlocal
echo ==================================================
echo   AMAZON REVIEWS PIPELINE AUTO-LAUNCHER
echo ==================================================

:: 1. ПІДЙОМ КОНТЕЙНЕРІВ
echo [1/4] Spinning up databases and monitoring...
docker-compose up -d minio mongo prometheus grafana
echo Waiting for services to stabilize...
timeout /t 15 /nobreak > NUL

:: 2. ЕТАП 1: ЗАВАНТАЖЕННЯ ДАНИХ (БРОНЗА -> СІЛВЕР)
:: Припустимо, у тебе є скрипт ініціалізації або первинного завантаження
echo [2/4] Running Initial Data Ingestion (Bronze to Silver)...
docker-compose run --rm app python app/main_bronze_to_silver.py

:: 3. ЕТАП 2: АНАЛІТИКА (СІЛВЕР -> ГОЛД)
:: Твій основний файл, який ми сьогодні мучили
echo [3/4] Running Analytics Processing (Silver to Gold)...
docker-compose run --rm app python app/main_silver_to_gold.py

:: 4. ФІНАЛ
echo [4/4] Pipeline completed successfully!
echo ==================================================
echo   INFRASTRUCTURE IS STILL RUNNING IN BACKGROUND
echo   To stop everything, run: docker-compose down
echo ==================================================
pause