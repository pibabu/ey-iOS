# /context_management/readme

llm has to start new conversation itself - user cannot do it!

use empty strings for positional argument   


## start_new_conversation.sh [handover_string]

Clears all conversation history and reloads all System Prompts.
The current conversation is not saved.

Trigger to run start_new_conversation.sh INSTANTLY with no handover_string:
- standalone user messages like "new conv" "nc" "nw chat"


## save_current_conversation.sh [filename] [project_path]

filename default: `conv_<timestamp>.json`
project_path default: `/llm/private/conversation_history/`

You are working on a Project? Save Conversation inside project/conversation/conversation_topic.md

## undo_last_messages.sh [count]

Removes the last N messages from current conversation.


---

you can manage messages during the conversation via api: "clear | replace_last | inject | remove_last"   
check docs if sensible