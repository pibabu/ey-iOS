# /context_management/readme

---explain setp and use cases----
before you run these scripts, make 

- undo_last_messages.sh:
Remove last N messages from conversation
Usage: undo_last_messages.sh <count>

- save_current_conversation.sh:
Usage:
save_current_conversation.sh                # saves to conv_<timestamp>.json
save_current_conversation.sh  custom.json    # saves to custom.json
Default save folder: /llm/private/conversation_history/

- start_new_conversation.sh
starts a new conversation and reloads system prompt with requirements and longterm_memory
