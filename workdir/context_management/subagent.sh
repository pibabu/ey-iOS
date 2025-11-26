#!/bin/bash
# subagent.sh

export API_BASE="${API_BASE:-http://${API_HOST}:${API_PORT}}"
export USER_HASH="${USER_HASH}"


runloopllm() {
    local initial_prompt="$1"
    local system_prompt_input="${2:-Execute the task iteratively. When done, provide a final condensed summary.}"
    local result_path="${3}"  
    local result_filename="${4}" 
    local max_iterations=5 
    
    # Check if system_prompt_input is a file, if so read it
    local system_prompt
    if [ -f "$system_prompt_input" ]; then
        system_prompt=$(cat "$system_prompt_input")
        echo "Loaded system prompt from file: $system_prompt_input"
    else
        system_prompt="$system_prompt_input"
    fi
    

    mkdir -p "/logs/subagent/"
    local log_file="/logs/subagent/loop_$(date +%Y%m%d_%H%M%S).log"

    echo "=== Multi-Turn LLM Loop ===" >> "$log_file"
    echo "Timestamp: $(date -Iseconds)" >> "$log_file"
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
        
        local response
        response=$(curl -s -X POST "${API_BASE}/api/llm/quick" \
            -H "Content-Type: application/json" \
            -d "$(jq -n \
                --arg prompt "$current_prompt" \
                --arg system "$system_prompt" \
                --arg hash "$USER_HASH" \
                --argjson history "$conversation_history" \
                '{prompt: $prompt, system_prompt: $system, user_hash: $hash, conversation_history: $history}' )")
        
        echo "$response" | jq '.' >> "$log_file"
        result=$(echo "$response" | jq -r '.result // ""')
        local is_complete
        is_complete=$(echo "$response" | jq -r '.complete // false')
        
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
    
    if [ -z "$final_result" ] && [ -n "$result" ]; then
        final_result="$result"
    fi
    
    echo "=== Final Output ===" >> "$log_file"
    echo "$final_result" >> "$log_file"
    echo "=== End ===" >> "$log_file"
    
    # Save final result to custom output if specified
    if [ -n "$result_path" ] && [ -n "$result_filename" ]; then
        mkdir -p "$result_path"
        local result_file="${result_path}/${result_filename}"
        echo "$final_result" > "$result_file"
        echo "Final result saved to: $result_file"
    fi
    
    echo "$final_result"
}