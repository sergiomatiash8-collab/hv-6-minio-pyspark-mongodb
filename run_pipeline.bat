@echo off
setlocal
echo ==================================================
echo   AMAZON REVIEWS PIPELINE AUTO-LAUNCHER
echo ==================================================

:: 1. ПІДЙОМ ВСІЄЇ ІНФРАСТРУКТУРИ
echo [1/4] Starting all services from docker-compose...
:: Команда 'up -d' без уточнення імен підніме ВСЕ, що описано в yaml файлі
docker-compose up -d

echo Waiting for services to stabilize (20s)...
timeout /t 20 /nobreak > NUL

:: 2. ЗАПУСК ЕТАПІВ
echo [2/4] Running Initial Data Ingestion...
docker-compose run --rm app python app/main_bronze_to_silver.py

echo [3/4] Running Analytics Processing...
docker-compose run --rm app python app/main_silver_to_gold.py

echo ==================================================
echo   PIPELINE FINISHED!
echo ==================================================
pause