#!/bin/bash
# Inject context messages into conversation without actual back-and-forth
# Useful for adding background info, priming, or "fake" conversation history


## weg?
export API_BASE="${API_BASE:-http://${API_HOST}:${API_PORT}}"
export USER_HASH="${USER_HASH}"

CONTEXT_FILE=$1

if [ ! -f "$CONTEXT_FILE" ]; then
    echo "❌ Context file not found: $CONTEXT_FILE"
    exit 1
fi

echo "💉 Injecting context from $CONTEXT_FILE..."

NEW_MESSAGES=$(cat "$CONTEXT_FILE")

response=$(curl -s -X POST "${API_BASE}/api/conversation/edit" \
    -H "Content-Type: application/json" \
    -d "{
        \"user_hash\": \"$USER_HASH\",
        \"action\": \"inject\",
        \"new_messages\": $NEW_MESSAGES
    }")

echo "$response" | jq '.'

if echo "$response" | jq -e '.status == "success"' > /dev/null; then
    added=$(echo "$response" | jq -r '.added_count')
    echo "✅ Injected $added message(s)"
else
    echo "❌ Failed to inject context"
    exit 1
fi