# AI Assistant with Bash Tool

A chatbot system that executes commands in isolated Docker environments, with conversation context automatically built from your project files

## Features

- **Isolated Environments**: Each user gets their own Docker container with own workspace 
- **Communication inside Network**: Container share Network and Volume 
- **Context-Aware**: Automatically loads project README, requirements, and file structure
- **Command Execution**: Run bash commands safely inside containers
- **Conversation Management**: Run Scripts inside Container to manage Conversation History, Save Files etc.