#!/bin/bash
# ------------------------------------------------------------
# Purpose : Fetches conversation data from the API and saves it
#           as a JSON file. Allows an optional filename parameter.
# Usage   :
#    save_current_conversation.sh                # saves to conv_<timestamp>.json
#    save_current_conversation.sh  custom.json    # saves to custom.json
# Notes   
#    - Default save folder: /llm/private/conversation_history/
# ------------------------------------------------------------
export API_BASE="${API_BASE:-http://${API_HOST}:${API_PORT}}"
export USER_HASH="${USER_HASH}"

# Validate that USER_HASH exists
if [ "$USER_HASH" = "unknown" ]; then
    echo "⚠️  WARNING: USER_HASH not set!"
fi

get_conversation_data() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local base_dir="/llm/private/conversation_history"
    local filename="$1"

    if [ -z "$filename" ]; then
        filename="conv_${timestamp}.json"
    fi

    filename="${base_dir}/${filename}"

    curl -s -X POST "${API_BASE}/api/conversation/export" \
        -H "Content-Type: application/json" \
        -d "{\"user_hash\": \"$USER_HASH\"}" > "$filename"

    echo "Saved to: $filename"
}
