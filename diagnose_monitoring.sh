#!/bin/bash
 
echo "🔍 Діагностика Prometheus + Grafana проблем"
echo "=============================================="
echo ""
 
# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color
 
# Функція для перевірки порту
check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${GREEN}✓${NC} Порт $port ($service) зайнятий - це нормально якщо сервіс запущений"
    else
        echo -e "${YELLOW}⚠${NC} Порт $port ($service) вільний - сервіс не запущений"
    fi
}
 
# Функція для перевірки контейнера
check_container() {
    local container=$1
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        local status=$(docker inspect --format='{{.State.Status}}' $container)
        if [ "$status" == "running" ]; then
            echo -e "${GREEN}✓${NC} Контейнер $container запущений"
        else
            echo -e "${RED}✗${NC} Контейнер $container не працює (status: $status)"
        fi
    else
        echo -e "${RED}✗${NC} Контейнер $container не знайдено"
    fi
}
 
# 1. Перевірка портів
echo "📡 Перевірка портів:"
check_port 9090 "Prometheus"
check_port 3000 "Grafana"
check_port 3100 "Loki"
check_port 8000 "ETL Metrics"
check_port 9100 "Node Exporter"
check_port 9216 "MongoDB Exporter"
echo ""
 
# 2. Перевірка контейнерів
echo "🐳 Перевірка Docker контейнерів:"
check_container "prometheus"
check_container "grafana"
check_container "loki"
check_container "promtail"
check_container "node-exporter"
echo ""
 
# 3. Перевірка мережі
echo "🌐 Перевірка Docker мережі:"
if docker network ls | grep -q "spark-network"; then
    echo -e "${GREEN}✓${NC} Мережа spark-network існує"
    echo "   Контейнери в мережі:"
    docker network inspect spark-network --format '{{range .Containers}}  - {{.Name}}{{println}}{{end}}'
else
    echo -e "${RED}✗${NC} Мережа spark-network не існує!"
    echo -e "${YELLOW}→${NC} Створюю мережу..."
    docker network create spark-network
fi
echo ""
 
# 4. Перевірка конфігурацій
echo "📝 Перевірка конфігурацій:"
if [ -f "monitoring/prometheus.yml" ]; then
    echo -e "${GREEN}✓${NC} monitoring/prometheus.yml існує"
else
    echo -e "${RED}✗${NC} monitoring/prometheus.yml не знайдено"
fi
 
if [ -d "monitoring/grafana/provisioning" ]; then
    echo -e "${GREEN}✓${NC} monitoring/grafana/provisioning існує"
else
    echo -e "${YELLOW}⚠${NC} monitoring/grafana/provisioning не існує (створюю...)"
    mkdir -p monitoring/grafana/provisioning/datasources
    mkdir -p monitoring/grafana/provisioning/dashboards
fi
echo ""
 
# 5. Тест підключення до Prometheus
echo "🔌 Тест підключення до сервісів:"
if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Prometheus доступний на http://localhost:9090"
else
    echo -e "${RED}✗${NC} Prometheus недоступний на http://localhost:9090"
fi
 
if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Grafana доступна на http://localhost:3000"
else
    echo -e "${RED}✗${NC} Grafana недоступна на http://localhost:3000"
fi
 
if curl -s http://localhost:8000/metrics > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} ETL metrics доступні на http://localhost:8000/metrics"
else
    echo -e "${YELLOW}⚠${NC} ETL metrics недоступні (app не запущений або metrics не налаштовані)"
fi
echo ""
 
# 6. Перевірка логів
echo "📋 Останні помилки в логах Prometheus:"
if docker ps --format '{{.Names}}' | grep -q "^prometheus$"; then
    docker logs prometheus --tail 10 2>&1 | grep -i "error\|warn" || echo -e "${GREEN}Немає помилок${NC}"
else
    echo -e "${YELLOW}Prometheus не запущений${NC}"
fi
echo ""
 
echo "📋 Останні помилки в логах Grafana:"
if docker ps --format '{{.Names}}' | grep -q "^grafana$"; then
    docker logs grafana --tail 10 2>&1 | grep -i "error\|warn" || echo -e "${GREEN}Немає помилок${NC}"
else
    echo -e "${YELLOW}Grafana не запущена${NC}"
fi
echo ""
 
# 7. Рекомендації
echo "💡 Рекомендації для виправлення:"
echo "=================================="
echo ""
echo "1. Якщо мережа не існувала - зараз створена. Перезапусти контейнери:"
echo -e "   ${YELLOW}docker-compose down && docker-compose up -d${NC}"
echo ""
echo "2. Якщо app метрики недоступні - додай в app сервіс порт 8000:"
echo -e "   ${YELLOW}ports:${NC}"
echo -e "   ${YELLOW}  - \"8000:8000\"${NC}"
echo ""
echo "3. Запусти моніторинг:"
echo -e "   ${YELLOW}docker-compose -f docker-compose.monitoring.yml up -d${NC}"
echo ""
echo "4. Перевір targets в Prometheus:"
echo -e "   ${YELLOW}http://localhost:9090/targets${NC}"
echo ""
echo "5. Зайди в Grafana (admin/admin):"
echo -e "   ${YELLOW}http://localhost:3000${NC}"
echo ""
echo "6. Якщо все ще проблеми - дивись логи:"
echo -e "   ${YELLOW}docker logs prometheus${NC}"
echo -e "   ${YELLOW}docker logs grafana${NC}"
echo ""
 
# 8. Автоматичне виправлення (опціонально)
echo "🔧 Автоматичне виправлення? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Зупиняю всі контейнери..."
    docker-compose -f docker-compose.monitoring.yml down
    docker-compose down
    
    echo "Видаляю volumes (опціонально)..."
    # docker volume prune -f
    
    echo "Створюю структуру директорій..."
    mkdir -p monitoring/grafana/provisioning/datasources
    mkdir -p monitoring/grafana/provisioning/dashboards
    mkdir -p monitoring/grafana/dashboards
    
    echo "Запускаю основні сервіси..."
    docker-compose up -d
    
    sleep 5
    
    echo "Запускаю моніторинг..."
    docker-compose -f docker-compose.monitoring.yml up -d
    
    sleep 10
    
    echo ""
    echo -e "${GREEN}✓ Готово! Перевір:${NC}"
    echo "   Prometheus: http://localhost:9090"
    echo "   Grafana: http://localhost:3000 (admin/admin)"
fi
 