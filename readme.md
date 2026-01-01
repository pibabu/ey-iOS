# Your Chatbot Just Got a Home Directory

Imagine an LLM that doesn't need explanations — because it can look around.


No more copy-pasting project structures into prompts. No more re-explaining your setup every conversation. 

Your LLM lives in a **dedicated Linux container** with full filesystem access, persistent memory, and the ability to execute commands. 

---

**It's a network, not just a container.** 
Every user's AI workspace can communicate with others through shared volumes and network access. Agents und Users can collaborate on projects, share data, or leave messages for each other—creating an ecosystem where isolated intelligence becomes collective capability.

---

The System Prompt consists of:

**1. `readme.md`** — The actual System Prompt  
**2. `req.md`** — Current state, tools, active projects, and alerts → links to other files
**3. `longterm_memory.md`** — Persistent information about the user  
**4. `tree workdir`** — Shows directory structure

---

## Features

### 🧠 Context Engineering 
No need to overload the context window with tools — inject them dynamically into the conversation by opening a file.

### 📦 UNIX Philosophy
Your file structure IS your LLM's memory. "Everything is a file."

### ⏰ Autonomous Scheduling 
Set up cron jobs for recurring tasks. Your LLM doesn't need you online to check emails, generate reports, or monitor websites.

### 💬 Conversation Management
Run scripts inside the container to manage conversation, like "Delete last messages", "Start new chat and handover context" or "Fork this conversation"

### 🤖 Subagents
Run subagents for tasks that would otherwise pollute the context window.

---

## "It's Just Bash" 

- **`mkdir mails/newsletter`** and **`touch recipients.csv newsletter.txt send_mail.sh readme.md`**
- **Run `subagent.sh`** to grep through logs, save condensed answer in file
- **`echo "Prefers metric system, dislikes 'think of it as' analogies" >> longterm_memory.md`** 
- **Run cron job `check_mail_agent.sh`**, alert with **`telegram.py`**
---

## Learn More


Check **[`workdir/readme.md`](workdir/readme.md)** for more info