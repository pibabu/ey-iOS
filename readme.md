A chatbot system that executes commands in isolated Docker environments, with conversation context automatically built from your project directories and files 


## Features

- **Context Engineering**: no need to overload token window with tools -> inject them dynamically into conversation by opening new dir
- **Context-Aware**: Automatically loads long-term memory, user settings and file structure into system prompt
- **Isolated Environments**: Each user gets their own Docker container with own workspace 
- **Communication inside Network**: Container share network and users can communicate via shared volume 
- **Command Execution**: Run bash commands safely inside containers; use Cron Jobs to automate tasks or LLM Calls
- **Conversation Management**: Run scripts inside Container to manage conversation history
- **Subagents**: Run Subagents for tasks that would otherwise pollute token window

## "It's just Bash"
- cd topics/coding/, cat README for context, run script.py with parameters
- run subagent.sh to grep through logs, save condensed answer in file
- add dynamic context by changing requirement.md -> injected into system prompt
- mkdir mails/newsletter and touch recipients.csv, newsletter.txt, send_mail.sh
- cat prompts/special-task.md -> inject prompt into current conversation


