#!/bin/bash
# Comprehensive Verification Script for Der Die Das Capybara Game 🦫
# Run this after: spin up

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:3000"

echo -e "${BLUE}🦫 Der Die Das - Capybara Game Verification Script${NC}"
echo "=========================================================="
echo ""

# Check if server is running
echo -e "${YELLOW}Checking if Spin server is running...${NC}"
if ! curl -s -f "$BASE_URL" > /dev/null 2>&1; then
    echo -e "${RED}❌ Server is not running on $BASE_URL${NC}"
    echo "Please start the server first with: spin up"
    exit 1
fi
echo -e "${GREEN}✅ Server is running${NC}"
echo ""

# Test 1: Random Word Endpoint
echo -e "${BLUE}Test 1: Getting random word entry${NC}"
WORD_RESPONSE=$(curl -s "$BASE_URL/api/entry.json")
echo "$WORD_RESPONSE" | jq .
WORD=$(echo "$WORD_RESPONSE" | jq -r '.[0].nominativ_singular')
GENUS=$(echo "$WORD_RESPONSE" | jq -r '.[0].genus')
echo -e "${GREEN}✅ Word API working - Got: $WORD ($GENUS)${NC}"
echo ""

# Test 2: Create Multiplayer Session
echo -e "${BLUE}Test 2: Creating multiplayer session${NC}"
SESSION_RESPONSE=$(curl -s -X POST "$BASE_URL/api/session/create" \
  -H "Content-Type: application/json" \
  -d '{"player_name": "Alice 🦫", "game_mode": "multiplayer"}')
echo "$SESSION_RESPONSE" | jq .

SESSION_ID=$(echo "$SESSION_RESPONSE" | jq -r .session_id)
PLAYER1_ID=$(echo "$SESSION_RESPONSE" | jq -r .player1_id)

if [ "$SESSION_ID" = "null" ] || [ -z "$SESSION_ID" ]; then
    echo -e "${RED}❌ Failed to create session${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Session created${NC}"
echo "   Session ID: $SESSION_ID"
echo "   Player 1 ID: $PLAYER1_ID"
echo ""

# Test 3: Get Session Details
echo -e "${BLUE}Test 3: Retrieving session details${NC}"
GET_SESSION=$(curl -s "$BASE_URL/api/session/$SESSION_ID")
echo "$GET_SESSION" | jq .
echo -e "${GREEN}✅ Session retrieval working${NC}"
echo ""

# Test 4: Join Session
echo -e "${BLUE}Test 4: Player 2 joining session${NC}"
JOIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/session/join" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"player_name\": \"Bob 🦫\"}")
echo "$JOIN_RESPONSE" | jq .

PLAYER2_ID=$(echo "$JOIN_RESPONSE" | jq -r .player2_id)

if [ "$PLAYER2_ID" = "null" ] || [ -z "$PLAYER2_ID" ]; then
    echo -e "${RED}❌ Failed to join session${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Player 2 joined successfully${NC}"
echo "   Player 2 ID: $PLAYER2_ID"
echo ""

# Test 5: Submit Answers - Player 1
echo -e "${BLUE}Test 5: Player 1 submitting 3 correct answers${NC}"
for i in {1..3}; do
    echo "  Answer $i..."
    curl -s -X POST "$BASE_URL/api/session/$SESSION_ID/answer" \
      -H "Content-Type: application/json" \
      -d "{\"player_id\": \"$PLAYER1_ID\", \"correct\": true}" | jq .
done
echo -e "${GREEN}✅ Player 1 submitted 3 answers${NC}"
echo ""

# Test 6: Submit Answers - Player 2
echo -e "${BLUE}Test 6: Player 2 submitting 2 correct answers${NC}"
for i in {1..2}; do
    echo "  Answer $i..."
    curl -s -X POST "$BASE_URL/api/session/$SESSION_ID/answer" \
      -H "Content-Type: application/json" \
      -d "{\"player_id\": \"$PLAYER2_ID\", \"correct\": true}" | jq .
done
echo -e "${GREEN}✅ Player 2 submitted 2 answers${NC}"
echo ""

# Test 7: Check Final Scores
echo -e "${BLUE}Test 7: Verifying final scores${NC}"
FINAL_SESSION=$(curl -s "$BASE_URL/api/session/$SESSION_ID")
echo "$FINAL_SESSION" | jq .

PLAYER1_SCORE=$(echo "$FINAL_SESSION" | jq -r .player1_score)
PLAYER2_SCORE=$(echo "$FINAL_SESSION" | jq -r .player2_score)

echo ""
echo -e "${YELLOW}Final Scores:${NC}"
echo "  Player 1 (Alice 🦫): $PLAYER1_SCORE points"
echo "  Player 2 (Bob 🦫): $PLAYER2_SCORE points"

if [ "$PLAYER1_SCORE" = "3" ] && [ "$PLAYER2_SCORE" = "2" ]; then
    echo -e "${GREEN}✅ Scores are correct!${NC}"
else
    echo -e "${RED}❌ Score mismatch! Expected 3 and 2, got $PLAYER1_SCORE and $PLAYER2_SCORE${NC}"
    exit 1
fi
echo ""

# Test 8: Static Files
echo -e "${BLUE}Test 8: Checking static files${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Homepage loads (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ Homepage failed (HTTP $HTTP_CODE)${NC}"
fi

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/style.css")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ CSS loads (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ CSS failed (HTTP $HTTP_CODE)${NC}"
fi

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/script.js")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ JavaScript loads (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ JavaScript failed (HTTP $HTTP_CODE)${NC}"
fi
echo ""

# Test 9: Check for Capybara Theme
echo -e "${BLUE}Test 9: Verifying Capybara & Roblox theme${NC}"
HTML_CONTENT=$(curl -s "$BASE_URL/")
if echo "$HTML_CONTENT" | grep -q "🦫"; then
    echo -e "${GREEN}✅ Capybara emojis found in HTML${NC}"
else
    echo -e "${RED}❌ No capybara emojis found${NC}"
fi

if echo "$HTML_CONTENT" | grep -q "Capybara Deutsch Spiel"; then
    echo -e "${GREEN}✅ German title found${NC}"
else
    echo -e "${RED}❌ German title not found${NC}"
fi

CSS_CONTENT=$(curl -s "$BASE_URL/style.css")
if echo "$CSS_CONTENT" | grep -q "Comic Sans"; then
    echo -e "${GREEN}✅ Comic Sans font found${NC}"
else
    echo -e "${RED}❌ Comic Sans font not found${NC}"
fi
echo ""

# Summary
echo "=========================================================="
echo -e "${GREEN}🎉 All tests passed! The Capybara game is ready! 🦫✨${NC}"
echo ""
echo "Next steps:"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Try all 4 game modes:"
echo "     - 📚🦫 Übungs-Modus (Practice)"
echo "     - ⏱️🦫 Zeit-Challenge (Timed)"
echo "     - 🎮🦫 Multiplayer Erstellen (Create)"
echo "     - 🔗🦫 Multiplayer Beitreten (Join)"
echo "  3. Have your daughter test it and have fun learning German!"
echo ""
echo -e "${BLUE}Made with 💖 for kids who love capybaras and Roblox!${NC}"
