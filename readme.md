# AI Assistant with Bash

A chatbot system that executes commands in isolated Docker environments, with conversation context automatically built from your project directories and files

## Features

- **Isolated Environments**: Each user gets their own Docker container with own workspace 
- **Communication inside Network**: Container/User share network and can communicate via shared volume 
- **Context-Aware**: Automatically loads project README, requirements, and file structure
- **Command Execution**: Run bash commands safely inside containers
- **Context Engineering**: Run Scripts inside Container to manage conversation history or use Bash Tool to create and manage files

## Philosophy - "Everything is a file"
- "Conversation management is just filesystem navigation. cd topics/coding/, read the README for context, run the scripts with parameters, grep through notes.md for history. It's all just directories and text files."