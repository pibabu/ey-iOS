#!/bin/bash

export API_BASE="${API_BASE:-http://${API_HOST}:${API_PORT}}"
export USER_HASH="${USER_HASH}"

runonetimellm() {
    local prompt="$1"
    local system_prompt_input="${2:-Execute the task and save results to a file using the bash tool.}"
    local output_path="${3:-/logs/single_shot/}"
    local filename="${4:-single_$(date +%Y%m%d_%H%M%S).log}"  


    local system_prompt
    if [ -f "$system_prompt_input" ]; then
        system_prompt=$(cat "$system_prompt_input")
        echo "Loaded system prompt from file: $system_prompt_input"
    else
        system_prompt="$system_prompt_input"
    fi
    mkdir -p "$output_path"

    local log_file="${output_path}/${filename}"

    echo "=== Single-Shot LLM Execution ===" >> "$log_file"
    echo "Timestamp: $(date -Iseconds)" >> "$log_file"
    echo "Output Path: $output_path" >> "$log_file"
    echo "Prompt: $prompt" >> "$log_file"
    echo "System Prompt: $system_prompt" >> "$log_file"
    echo "---" >> "$log_file"

    local response
    response=$(curl -s -X POST "${API_BASE}/api/llm/quick" \
        -H "Content-Type: application/json" \
        -d "$(jq -n \
            --arg prompt "$prompt" \
            --arg system "$system_prompt" \
            --arg hash "$USER_HASH" \
            '{prompt: $prompt, system_prompt: $system, user_hash: $hash}'
        )")

  
    echo "$response" | jq '.' >> "$log_file"


    local result
    result=$(echo "$response" | jq -r '.result')

    echo "=== End ===" >> "$log_file"
    echo "" >> "$log_file"

    echo "$result"
}