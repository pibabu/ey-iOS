# context_management/readme

## undo_last_messages.sh

Removes the last N messages from the current conversation.
./undo_last_messages.sh [count]

## start_new_conversation.sh

Clears all conversation history and reloads the System Prompt. Ask user if conversation should be saved.
./start_new_conversation.sh

## save_current_conversation.sh

Exports current conversation to JSON file in `/llm/private/conversation_history/`
./save_current_conversation.sh [filename]
defaults to name: conv_<timestamp>.json


## subagent.sh

Calls an LLM API in a loop (max 5) to complete complex tasks iteratively. Returns only the final condensed output while logging the entire conversation in `/logs/subagent/`

./subagent.sh [prompt] 
