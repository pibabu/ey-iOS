# /context_management/readme

use empty strings for positional argument   
during conversation: wait for user confirmation before you run script

# Context Management Trigger

- user says "run -context- as loop": read ./agent_loop/readme.md


## start_new_conversation.sh [handover_string]

Clears all conversation history and reloads all System Prompts.
The current conversation is not saved.
to disable req, send as handover_string:
"DONT call bash_tool immediatly as stated in req; in fact, ignore req entirely"

## save_current_conversation.sh [filename] [project_path]

filename default: `conv_<timestamp>.json`
project_path default: `/llm/private/conversation_history/`

You are working on a Project? Save Conversation inside project/conversation/self_explainig_name_:_short_summary_of_conversation.md

## undo_last_messages.sh [count]

Removes the last N messages from the current conversation.



# llm api calls 



You can send file or string as system_prompt parameter. Use: ./readme.md or create own

## subagent.sh [your_prompt] [system_prompt] [output_path] [output_filename]

Calls an LLM API in a loop (max 5). 
Returns only the final condensed output.
Logs entire agent loop in `/logs/subagent/`

## single_shot_llm_call.sh [your_prompt] [system_prompt] [output_path] [output_filename]

Output default: `/logs/single_shot`

