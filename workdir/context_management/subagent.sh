# subagent.sh
#!/bin/bash

export API_BASE="${API_BASE:-http://${API_HOST}:${API_PORT}}"
export USER_HASH="${USER_HASH}"
export LOG_DIR="${LOG_DIR:-/logs/subagent/}"

mkdir -p "$LOG_DIR"

runloopllm() {
    local initial_prompt="$1"
    local system_prompt="${2:-Execute the task iteratively. When done, provide a final condensed summary.}"
    local max_iterations="${3:-5}"
    local log_file="${LOG_DIR}/loop_$(date +%Y%m%d_%H%M%S).log"
    
    echo "=== Multi-Turn LLM Loop ===" >> "$log_file"
    echo "Timestamp: $(date -Iseconds)" >> "$log_file"
    echo "Initial Prompt: $initial_prompt" >> "$log_file"
    echo "===" >> "$log_file"
    echo "" >> "$log_file"
    
    local conversation_history="[]"
    local current_prompt="$initial_prompt"
    local final_result=""
    
    for ((i=1; i<=max_iterations; i++)); do
        echo "--- Iteration $i ---" >> "$log_file"
        
        # Call /quick with conversation history
        local response=$(curl -s -X POST "${API_BASE}/api/llm/quick" \
            -H "Content-Type: application/json" \
            -d "$(jq -n \
                --arg prompt "$current_prompt" \
                --arg system "$system_prompt" \
                --arg hash "$USER_HASH" \
                --argjson history "$conversation_history" \
                '{prompt: $prompt, system_prompt: $system, user_hash: $hash, conversation_history: $history}'
            )")
        
        echo "$response" | jq '.' >> "$log_file"
        
        local result=$(echo "$response" | jq -r '.result')
        local is_complete=$(echo "$response" | jq -r '.complete // false')
        
        # Update history with this turn
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
        
        if [ $i -lt $max_iterations ]; then
            current_prompt="Continue with the next step."
        else
            current_prompt="Provide final condensed summary of all work done."
            final_result="$result"
        fi
    done
    
    echo "=== Final Output ===" >> "$log_file"
    echo "$final_result" >> "$log_file"
    echo "=== End ===" >> "$log_file"
    
    echo "$final_result"
}