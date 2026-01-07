# Your Chatbot Just Got a Home Directory

Imagine an LLM that doesn't need explanations — **because it can look around**


Your LLM lives in a **dedicated Linux container** with full access, persistent memory, and the ability to execute commands. 


---

**The System Prompt consists of:**

**1. `readme.md`** — describes the core architecture    
**2. `req.md`** — Current state, tools, projects, and alerts → links to other files and is constantly updated   
**3. `tree workdir`** — Shows directory structure   
**4. `Overwrite Settings`** — Context handed over from previous conversation or scripts


---

## Features

### 🧠 Context Engineering 
No need to overload the context window with tools — inject them dynamically into the conversation by opening a file.

### 📦 Everything is a File
Files store memory and tools. Bash grants agency.   

### ⏰ Autonomous Scheduling 
Set up cron jobs for recurring tasks. Your LLM doesn't need you online to check emails, generate reports, or monitor websites.

### 💬 Conversation Management
Run scripts inside the container to manage conversation, like "Delete last messages", "Start new chat and handover context" or "Fork this conversation"

### 🤖 Subagents
Run subagents for tasks that would otherwise pollute the context window.

### 🕸️ Shared Network
Agents und Users can collaborate on projects, share data, or leave messages for each other

---



## "It's Just Bash" 

- **`mkdir mails/newsletter`** and **`touch recipients.csv newsletter.txt send_mail.sh readme.md`**
- **`cat agent_loop`**, find the right prompting technique like ReAct 
- **`echo "Prefers metric system, dislikes 'think of it as' analogies" >> longterm_memory.md`** 
- Run cron job **`check_mail_agent.sh`**, alert with **`telegram.py`**
---


## Learn More


Check **[`workdir/readme.md`](workdir/readme.md)**, the opening file of the System Prompt