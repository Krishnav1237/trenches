#!/bin/bash

# Trenches AI Agent Social Network - Service Startup Script
# This script starts all required services for the platform

set -e

echo "🚀 Starting Trenches Platform Services..."
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}⚠️  Port $1 is already in use${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Port $1 is available${NC}"
        return 0
    fi
}

# Check required ports
echo -e "\n${BLUE}Checking required ports...${NC}"
check_port 8080 # Go Backend
check_port 8081 # Python Personality API
check_port 5432 # PostgreSQL
check_port 6379 # Redis
check_port 7687 # Neo4j

# Start PostgreSQL (if not running)
echo -e "\n${BLUE}Starting PostgreSQL...${NC}"
if ! pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
    echo "Starting PostgreSQL..."
    # Adjust based on your system
    # sudo systemctl start postgresql
    # or: brew services start postgresql
else
    echo -e "${GREEN}✅ PostgreSQL is running${NC}"
fi

# Start Redis (if not running)
echo -e "\n${BLUE}Starting Redis...${NC}"
if ! redis-cli ping >/dev/null 2>&1; then
    echo "Starting Redis..."
    redis-server --daemonize yes
else
    echo -e "${GREEN}✅ Redis is running${NC}"
fi

# Start Neo4j (if not running)
echo -e "\n${BLUE}Starting Neo4j...${NC}"
if ! curl -s http://localhost:7474 >/dev/null 2>&1; then
    echo "Starting Neo4j..."
    # neo4j start
else
    echo -e "${GREEN}✅ Neo4j is running${NC}"
fi

# Start Go Backend
echo -e "\n${BLUE}Starting Go Backend API (port 8080)...${NC}"
cd backend
go run main.go websocket.go &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
cd ..

# Wait a moment for backend to initialize
sleep 2

# Start Python Personality API
echo -e "\n${BLUE}Starting Python Personality API (port 8081)...${NC}"
cd agents/api
python3 personality_api.py &
PERSONALITY_PID=$!
echo -e "${GREEN}✅ Personality API started (PID: $PERSONALITY_PID)${NC}"
cd ../..

# Wait a moment for personality API to initialize
sleep 2

# Start News Scheduler (optional)
echo -e "\n${BLUE}Starting News Scheduler...${NC}"
cd agents
python3 news_scheduler.py &
NEWS_PID=$!
echo -e "${GREEN}✅ News Scheduler started (PID: $NEWS_PID)${NC}"
cd ..

# Wait a moment for news scheduler to initialize
sleep 2

# Start Frontend (optional - usually run separately in dev mode)
echo -e "\n${BLUE}Frontend should be started separately with:${NC}"
echo "  cd Frontend/trenches-pixel-perfect-main"
echo "  npm run dev"

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 All services started successfully!${NC}"
echo ""
echo "Service URLs:"
echo "  • Go Backend API:        http://localhost:8080"
echo "  • Personality API:       http://localhost:8081"
echo "  • News Scheduler:        Running in background"
echo "  • PostgreSQL:            localhost:5432"
echo "  • Redis:                 localhost:6379"
echo "  • Neo4j:                 http://localhost:7474"
echo ""
echo "To stop services:"
echo "  kill $BACKEND_PID $PERSONALITY_PID $NEWS_PID"
echo ""
echo -e "${BLUE}Press Ctrl+C to stop all services${NC}"

# Wait for user interrupt
wait
