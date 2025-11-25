# /context_management/readme

## rules

- If you work on a project, you should save output in current_project/
- you can save files in /temp when unsure, dont ask user


## start_new_conversation.sh [handover_prompt]

Clears all conversation history and reloads all System Prompts.
You can handover data to new conversation.
The current conversation is not saved.

## save_current_conversation.sh [filename] [project_path]

filename default: `conv_<timestamp>.json`
project_path default: `/llm/private/conversation_history/`

You are working on a Project? Save Conversation inside project_dir/conversation/selfexplainig_name_:_short_summary_of_conversation.md

## undo_last_messages.sh [count]

Removes the last N messages from the current conversation.



# llm api calls 



You should send files as system_prompt parameter. Use: llm/private/readme.md or create own

## subagent.sh [your_prompt] [system_prompt] [output_path] [output_filename]

Calls an LLM API in a loop (max 5) to complete complex tasks iteratively. 
Returns only the final condensed output to:
- you as tool output
- 
- logs entire conversation in `/logs/subagent/`

## single_shot_llm_call.sh [your_prompt] [system_prompt] [output_path] [output_filename]

default: `/logs/single_shot`

