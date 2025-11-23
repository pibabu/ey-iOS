# context_management/readme

## undo_last_messages.sh

Removes the last N messages from the current conversation.
./undo_last_messages.sh [count]

Default count: 1

## start_new_conversation.sh

Clears all conversation history and reloads the System Prompt. Ask user if conversation should be saved.
./start_new_conversation.sh


## save_current_conversation.sh

Exports current conversation to JSON file in `/llm/private/conversation_history/`
./save_current_conversation.sh [filename]

Default filename: `conv_<timestamp>.json`
