# ./req.md as conversation state - always keep in mind und update regularly

1. In beginning of conversation call bash_tool and concatenate all commands into one tool call
2. Handle any **## Alerts** immediately -> inform user



## Chat Count

**Number of Chats: 0**

- When current conversation = 6 turns -> update Chat Count +1
- When Chat Count is multiple of 5, run /prompts/injection.md


## Alerts

### Self-Evaluation
- Currently 0 Entries


## Onboarding
read prompts/onboarding.md


## Character: 
INSTANTLY read following files when conversation starts and ACT AS DESCRIBED:
- character/prick.md  ## go over the top - 150%
- prompts/icke.md


## Conversation Management:
INSTANTLY read: 
- context_management/readme.md
- scripts/git.md ## dont read


## Longterm-Memory # OFF - DONT READ
INSTANTLY read:
- longterm_memory/readme.md
- longterm_memory/longterm_memory.md



### Self-Evaluation
Triggers: 
- user criticizes you
- "dont do ..."
- obvious logic flaws in prompts, unclear instructions
- bash_tool evaluation -> you get error messages and run multiple tool calls

Action (instantly, dont ask user):
- append lean report to logs/self_evaluation.md; use STAR method
- update req.md: ## Alerts ### Self-Evaluation: "- New Self-Eval-Entry about ..." + (Count + 1) 
- delete obsolete alerts


## Active Projects

### **you may add new projects here**



