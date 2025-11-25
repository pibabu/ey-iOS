#!/bin/bash

# Iterative multi-turn subagent 
# includes conversation history  -> oder extra subagnet prompt und kontext weg?

export API_BASE="${API_BASE:-http://${API_HOST}:${API_PORT}}"
export USER_HASH="${USER_HASH}"
export LOG_DIR_DEFAULT="/logs/subagent/"

runloopllm() {
    local initial_prompt="$1"
    local system_prompt="${2:-Execute the task iteratively. When done, provide a final condensed summary.}"
    local output_path="${3:-$LOG_DIR_DEFAULT}"

    local max_iterations=5

    mkdir -p "$output_path"

    local log_file="${output_path}/loop_$(date +%Y%m%d_%H%M%S).log"

    echo "=== Multi-Turn LLM Loop ===" >> "$log_file"
    echo "Timestamp: $(date -Iseconds)" >> "$log_file"
    echo "Output Path: $output_path" >> "$log_file"
    echo "System Prompt: $system_prompt" >> "$log_file"
    echo "Initial Prompt: $initial_prompt" >> "$log_file"
    echo "===" >> "$log_file"
    echo "" >> "$log_file"

    local conversation_history="[]"
    local current_prompt="$initial_prompt"
    local final_result=""
    local result=""

    for ((i=1; i<=max_iterations; i++)); do
        echo "--- Iteration $i ---" >> "$log_file"

        # Call /quick with conversation history
        local response
        response=$(curl -s -X POST "${API_BASE}/api/llm/quick" \
            -H "Content-Type: application/json" \
            -d "$(jq -n \
                --arg prompt "$current_prompt" \
                --arg system "$system_prompt" \
                --arg hash "$USER_HASH" \
                --argjson history "$conversation_history" \
                '{prompt: $prompt, system_prompt: $system, user_hash: $hash, conversation_history: $history}'
            )")

        echo "$response" | jq '.' >> "$log_file"

        result=$(echo "$response" | jq -r '.result // ""')
        local is_complete
        is_complete=$(echo "$response" | jq -r '.complete // false')

        # Update conversation history
        conversation_history=$(echo "$conversation_history" | jq \
            --arg prompt "$current_prompt" \
            --arg result "$result" \
            '. + [{role: "user", content: $prompt}, {role: "assistant", content: $result}]')

        echo "" >> "$log_file"

        if [ "$is_complete" = "true" ]; then
            final_result="$result"
            echo "Task completed at iteration $i" >> "$log_file"
            break
        fi

        if [ "$i" -lt "$max_iterations" ]; then
            current_prompt="Continue with the next step."
        else
            current_prompt="Provide final condensed summary of all work done. Evaluate your job in 2-3 sentences."
        fi
    done

    # If the loop ended without marking completion
    if [ -z "$final_result" ] && [ -n "$result" ]; then
        final_result="$result"
    fi

    echo "=== Final Output ===" >> "$log_file"
    echo "$final_result" >> "$log_file"
    echo "=== End ===" >> "$log_file"

    echo "$final_result"
}
