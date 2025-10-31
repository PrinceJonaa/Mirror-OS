#!/bin/bash
# Test backend API endpoints for Phase 5

echo "=== Testing Backend API Endpoints ==="
echo ""

BASE_URL="http://localhost:8000"

# Test health check
echo "1. Testing root endpoint..."
curl -s "${BASE_URL}/" | head -c 200
echo ""
echo ""

# Test lattice points
echo "2. Testing /api/analytics/lattice-points..."
curl -s "${BASE_URL}/api/analytics/lattice-points" | python3 -m json.tool | head -30
echo ""
echo ""

# Test collapse map
echo "3. Testing /api/analytics/collapse-map..."
curl -s "${BASE_URL}/api/analytics/collapse-map" | python3 -m json.tool | head -30
echo ""
echo ""

# Test runs list
echo "4. Testing /api/runs..."
curl -s "${BASE_URL}/api/runs" | python3 -m json.tool | head -30
echo ""
echo ""

echo "=== Test Complete ==="
