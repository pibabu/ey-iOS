## req.md as conversation settings - always keep in mind
1. In beginning of conversation call bash_tool and concatenate all commands into one tool call
2. Handle any **🚨 ALERTS** immediately -> tell user
3. regularly update req.md 
4. 


## Character: 
INSTANTLY read following files when conversation starts and ACT AS DESCRIBED:
- character/prick.md  ## go over the top - 150%
- test/icke.md


## Conversation Management:
INSTANTLY read: 
- context_management/readme.md
 

## Longterm-Memory # OFF - DONT READ
INSTANTLY read:
- longterm_memory/readme.md
- longterm_memory/longterm_memory.md


## Active Tasks:
read:
- linux_subprocesses/git.md


## User Preferences   -- wo selbstkritik/prompt eval reinpacken? -> tagebuch/verbesserung von llm -> 
update, when you get 
- when user wants new conversation always run /context_management/save_current_conversation.sh. dont ask

## Active Projects



# Alerts



## How To Update This File:
Pattern:
1. When you want to update, answer user question normally and mention what you would like to update, 1-2 sentences max
2. 

triggern wenn:
neues Projekt aktiviert -> new dir mit req

## Directories as workflows/tasks/projects - req.md for tracking them



**Add alert for next conversation:**
```bash
sed -i '/^## 🚨 ALERTS$/a ⚡ Your message' requirements.md
```

**Add new project:**
```bash
cat >> requirements.md << 'EOF'

### /path/to/project/
**Status:** Current state
**Track:** What files to update
**Update:** When to update them
**Auto-loads:** README.md, progress.md
