#!/bin/bash
# save_current_conversation.sh
# Allows optional filename and path parameters.

# Default save folder: /llm/private/conversation_history/

export API_BASE="${API_BASE:-http://${API_HOST}:${API_PORT}}"
export USER_HASH="${USER_HASH}"

# Validate that USER_HASH exists
if [ "$USER_HASH" = "unknown" ]; then
    echo "⚠️  WARNING: USER_HASH not set!"
fi

get_conversation_data() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local default_dir="/llm/private/conversation_history"
    local filename="$1"
    local save_path="$2"
    
    # Determine the directory to use
    if [ -z "$save_path" ]; then
        save_path="$default_dir"
    fi
    
    # Ensure the directory exists
    if [ ! -d "$save_path" ]; then
        echo "Creating directory: $save_path"
        mkdir -p "$save_path"
    fi
    
    # Determine the filename
    if [ -z "$filename" ]; then
        filename="conv_${timestamp}.json"
    fi
    
    # Construct full path
    local full_path="${save_path}/${filename}"
    
    # Fetch and save the conversation data
    curl -s -X POST "${API_BASE}/api/conversation/export" \
        -H "Content-Type: application/json" \
        -d "{\"user_hash\": \"$USER_HASH\"}" > "$full_path"
    
    if [ $? -eq 0 ]; then
        echo "✓ Saved to: $full_path"
    else
        echo "✗ Error saving conversation"
        return 1
    fi
}

# Call the function with provided arguments
get_conversation_data "$1" "$2"