# /context_management/readme

## start_new_conversation.sh [handover_prompt]

Clears all conversation history and reloads the System Prompt.
You can handover data to new conversation.

## save_current_conversation.sh [filename] [project_path]

filename default: `conv_<timestamp>.json`
project_path default: `/llm/private/conversation_history/`

You are working on a Project? Save Conversation inside project_dir/conversation/

## undo_last_messages.sh [count]

Removes the last N messages from the current conversation.



# llm api calls // --> speiechert files in timestamp.txt -> llm fehlt context, kein name!  -> 4 parameter??

You can 

## subagent.sh [your_prompt] [system_prompt] [output_path]

Calls an LLM API in a loop (max 5) to complete complex tasks iteratively. Returns only the final condensed output while logging the entire conversation in `/logs/subagent/`

## single_shot_llm_call.sh [your_prompt] [system_prompt] [output_path]

default: /logs/single_shot

