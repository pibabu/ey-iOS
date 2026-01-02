#!/bin/bash


### add: file as parameter

#   ./start_new_conversation.sh
#   ./start_new_conversation.sh "Custom instructions here. Appends to System Prompt"

export API_BASE="${API_BASE:-http://${API_HOST}:${API_PORT}}"
export USER_HASH="${USER_HASH}"

# Get custom append text from first argument (if provided)
APPEND_TEXT="${1:-}"

echo "🔄 Starting new conversation..."

# Build JSON payload
if [ -n "$APPEND_TEXT" ]; then
    echo "📝 Custom system prompt append: $APPEND_TEXT"
    PAYLOAD=$(jq -n \
        --arg user_hash "$USER_HASH" \
        --arg append "$APPEND_TEXT" \
        '{
            user_hash: $user_hash,
            action: "clear",
            system_prompt_append: $append
        }')
else
    PAYLOAD=$(jq -n \
        --arg user_hash "$USER_HASH" \
        '{
            user_hash: $user_hash,
            action: "clear"
        }')
fi

response=$(curl -s -X POST "${API_BASE}/api/conversation/edit" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

echo "$response" | jq '.'

if echo "$response" | jq -e '.status == "success"' > /dev/null; then
    echo "✅ Conversation cleared successfully"
    
    if [ -n "$APPEND_TEXT" ]; then
        echo "✅ Custom system prompt text set"
    fi
    
    echo "📝 Starting fresh - next message will be the first"
else
    echo "❌ Failed to clear conversation"
    exit 1
fi