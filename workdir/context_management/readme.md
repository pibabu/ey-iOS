# /context_management/readme

## start_new_conversation.sh

Clears all conversation history and reloads the System Prompt. Ask user if conversation should be saved.

## save_current_conversation.sh [filename] [project_path]

filename default: `conv_<timestamp>.json`
project_path default: `/llm/private/conversation_history/`

You are working on a Project? Save Conversation inside project_dir/conversation/

## subagent.sh [prompt] 

Calls an LLM API in a loop (max 5) to complete complex tasks iteratively. Returns only the final condensed output while logging the entire conversation in `/logs/subagent/`


## undo_last_messages.sh [count]

Removes the last N messages from the current conversation.

