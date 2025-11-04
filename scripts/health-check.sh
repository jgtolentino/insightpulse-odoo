#!/bin/bash
#########################################################################
# Health Check Script for InsightPulse AI
# Verifies all services are running and healthy
# Usage: ./health-check.sh [--verbose]
#########################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

VERBOSE=0
if [ "$1" = "--verbose" ]; then
    VERBOSE=1
fi

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

check() {
    SERVICE=$1
    URL=$2
    EXPECTED_CODE=${3:-200}
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    if [ $VERBOSE -eq 1 ]; then
        echo -n "Checking $SERVICE... "
    fi
    
    RESPONSE=$(curl -s -w "\n%{http_code}" --max-time 10 "$URL" 2>/dev/null)
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "$EXPECTED_CODE" ]; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        if [ $VERBOSE -eq 1 ]; then
            echo -e "${GREEN}✓ PASSED${NC} (HTTP $HTTP_CODE)"
            if [ -n "$BODY" ]; then
                echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY" | head -c 100
            fi
        else
            echo -e "${GREEN}✓${NC} $SERVICE"
        fi
        return 0
    else
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        if [ $VERBOSE -eq 1 ]; then
            echo -e "${RED}✗ FAILED${NC} (HTTP $HTTP_CODE)"
            echo "$BODY" | head -c 200
        else
            echo -e "${RED}✗${NC} $SERVICE (HTTP $HTTP_CODE)"
        fi
        return 1
    fi
}

check_docker() {
    CONTAINER=$1
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    if [ $VERBOSE -eq 1 ]; then
        echo -n "Checking Docker container: $CONTAINER... "
    fi
    
    if docker ps | grep -q "$CONTAINER"; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        STATUS=$(docker ps --format "table {{.Status}}" --filter "name=$CONTAINER" | tail -n1)
        if [ $VERBOSE -eq 1 ]; then
            echo -e "${GREEN}✓ RUNNING${NC} ($STATUS)"
        else
            echo -e "${GREEN}✓${NC} Docker: $CONTAINER"
        fi
        return 0
    else
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        if [ $VERBOSE -eq 1 ]; then
            echo -e "${RED}✗ NOT RUNNING${NC}"
        else
            echo -e "${RED}✗${NC} Docker: $CONTAINER"
        fi
        return 1
    fi
}

check_disk() {
    MOUNT=$1
    THRESHOLD=${2:-80}
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    if [ $VERBOSE -eq 1 ]; then
        echo -n "Checking disk usage: $MOUNT... "
    fi
    
    USAGE=$(df -h "$MOUNT" | tail -n1 | awk '{print $5}' | sed 's/%//')
    
    if [ "$USAGE" -lt "$THRESHOLD" ]; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        if [ $VERBOSE -eq 1 ]; then
            echo -e "${GREEN}✓ OK${NC} (${USAGE}% used)"
        else
            echo -e "${GREEN}✓${NC} Disk: $MOUNT (${USAGE}%)"
        fi
        return 0
    else
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        if [ $VERBOSE -eq 1 ]; then
            echo -e "${RED}✗ WARNING${NC} (${USAGE}% used, threshold: ${THRESHOLD}%)"
        else
            echo -e "${RED}✗${NC} Disk: $MOUNT (${USAGE}% - WARNING)"
        fi
        return 1
    fi
}

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}InsightPulse AI Health Check${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

#########################################################################
# 1. Production Services Health Checks
#########################################################################
echo -e "${BLUE}[1/5] Production Services${NC}"
echo "-----------------------------------"

check "Landing Page" "https://insightpulseai.net" 200
check "Odoo ERP" "https://erp.insightpulseai.net/web/health" 200
check "MCP Coordinator" "https://mcp.insightpulseai.net/health" 200
check "Superset" "https://superset.insightpulseai.net/health" 200
check "OCR Service" "https://ocr.insightpulseai.net/health" 200

echo ""

#########################################################################
# 2. Docker Containers (if on droplet)
#########################################################################
if command -v docker &> /dev/null; then
    echo -e "${BLUE}[2/5] Docker Containers${NC}"
    echo "-----------------------------------"
    
    check_docker "odoo"
    check_docker "odoo-postgres"
    check_docker "ocr"
    
    echo ""
else
    echo -e "${YELLOW}[2/5] Docker not available (skipping)${NC}"
    echo ""
fi

#########################################################################
# 3. Database Connectivity
#########################################################################
if command -v docker &> /dev/null && docker ps | grep -q "odoo-postgres"; then
    echo -e "${BLUE}[3/5] Database Connectivity${NC}"
    echo "-----------------------------------"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    if [ $VERBOSE -eq 1 ]; then
        echo -n "Checking PostgreSQL connection... "
    fi
    
    if docker exec odoo-postgres psql -U odoo -d odoo -c "SELECT 1;" > /dev/null 2>&1; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        
        # Get database size
        DB_SIZE=$(docker exec odoo-postgres psql -U odoo -d odoo -t -c "SELECT pg_size_pretty(pg_database_size('odoo'));" | xargs)
        
        if [ $VERBOSE -eq 1 ]; then
            echo -e "${GREEN}✓ CONNECTED${NC} (Size: $DB_SIZE)"
        else
            echo -e "${GREEN}✓${NC} PostgreSQL ($DB_SIZE)"
        fi
    else
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        if [ $VERBOSE -eq 1 ]; then
            echo -e "${RED}✗ CONNECTION FAILED${NC}"
        else
            echo -e "${RED}✗${NC} PostgreSQL"
        fi
    fi
    
    echo ""
else
    echo -e "${YELLOW}[3/5] Database not available (skipping)${NC}"
    echo ""
fi

#########################################################################
# 4. Disk Space
#########################################################################
echo -e "${BLUE}[4/5] Disk Space${NC}"
echo "-----------------------------------"

check_disk "/" 80
check_disk "/backup" 90 2>/dev/null || echo -e "${YELLOW}⚠${NC} /backup not mounted"

echo ""

#########################################################################
# 5. SSL Certificates
#########################################################################
echo -e "${BLUE}[5/5] SSL Certificates${NC}"
echo "-----------------------------------"

check_ssl() {
    DOMAIN=$1
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    if [ $VERBOSE -eq 1 ]; then
        echo -n "Checking SSL: $DOMAIN... "
    fi
    
    EXPIRY=$(echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:443" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
    
    if [ -n "$EXPIRY" ]; then
        EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s 2>/dev/null || date -j -f "%b %d %T %Y %Z" "$EXPIRY" +%s 2>/dev/null)
        CURRENT_EPOCH=$(date +%s)
        DAYS_LEFT=$(( ($EXPIRY_EPOCH - $CURRENT_EPOCH) / 86400 ))
        
        if [ "$DAYS_LEFT" -gt 30 ]; then
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
            if [ $VERBOSE -eq 1 ]; then
                echo -e "${GREEN}✓ VALID${NC} ($DAYS_LEFT days remaining)"
            else
                echo -e "${GREEN}✓${NC} $DOMAIN ($DAYS_LEFT days)"
            fi
            return 0
        else
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
            if [ $VERBOSE -eq 1 ]; then
                echo -e "${YELLOW}⚠ EXPIRING SOON${NC} ($DAYS_LEFT days remaining)"
            else
                echo -e "${YELLOW}⚠${NC} $DOMAIN ($DAYS_LEFT days - RENEW SOON)"
            fi
            return 1
        fi
    else
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        if [ $VERBOSE -eq 1 ]; then
            echo -e "${RED}✗ FAILED${NC}"
        else
            echo -e "${RED}✗${NC} $DOMAIN"
        fi
        return 1
    fi
}

check_ssl "insightpulseai.net"
check_ssl "erp.insightpulseai.net"
check_ssl "mcp.insightpulseai.net"
check_ssl "superset.insightpulseai.net"
check_ssl "ocr.insightpulseai.net"

echo ""

#########################################################################
# Summary
#########################################################################
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Health Check Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Total Checks: $TOTAL_CHECKS"
echo -e "Passed: ${GREEN}$PASSED_CHECKS${NC}"
echo -e "Failed: ${RED}$FAILED_CHECKS${NC}"
echo ""

HEALTH_PERCENTAGE=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))

if [ $HEALTH_PERCENTAGE -eq 100 ]; then
    echo -e "${GREEN}✅ System Health: 100% - All services operational${NC}"
    exit 0
elif [ $HEALTH_PERCENTAGE -ge 80 ]; then
    echo -e "${YELLOW}⚠️  System Health: ${HEALTH_PERCENTAGE}% - Some issues detected${NC}"
    exit 1
else
    echo -e "${RED}🚨 System Health: ${HEALTH_PERCENTAGE}% - CRITICAL ISSUES${NC}"
    exit 2
fi
