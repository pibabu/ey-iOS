# A Chatbot That Understands Your Project 
**Because it runs inside it.**

No more "here's my project structure again" or copy-pasting context into every new chat. 

**Prompts become files. Workflows become directories.**

Everything follows UNIX principles: small, composable pieces that let you engineer LLM interactions the same way you'd build any reliable system.

---

## Features

### 🧠 Context Engineering
No need to overload the context window with tools — inject them dynamically into the conversation by opening a file.

### 📚 Context-Aware
Automatically loads long-term memory, global state, and file structure into the system prompt. Inject System Messages or Alerts in current conversation.

### 🔒 Isolated Environments
Each user gets their own Debian container with a dedicated workspace and internet access.

### 🌐 Communication Inside Network
Containers share a network, and users can communicate via a shared volume.

### ⚙️ Command Execution
Run bash commands safely inside containers. Use Cron Jobs to automate tasks or LLM calls.

### 💬 Conversation Management
Run scripts inside the container to manage conversation, like "Delete last Messages" or "Start new Conversation and handover Context"

### 🤖 Subagents
Run subagents for tasks that would otherwise pollute the context window.

---

## "It's Just Bash"

- **`mkdir mails/newsletter`** and **`touch recipients.csv, newsletter.txt, send_mail.sh, readme.md`**
- **`cd topics/coding/`**, **`cat readme.md`** for context, **`run script.py`** with parameters
- **Run `subagent.sh`** to grep through logs, save condensed answer in file
- **Add dynamic context** by changing `req.md` → automatically injected into system prompt
- **Run `start_new_conversation.sh`** → start new Conversation and send Context as parameter

---

## Learn More


Check **[`workdir/readme.md`](workdir/readme.md)** for more info