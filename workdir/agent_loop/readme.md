# agent_loop/readme

script to call: context_management/start_new_conversation.sh [str]

-> you send: "req is DISABLED, read current_project_name/readme.md instead"     

## Agent Loop Count: 0

IMPORTANT - max allowed loops: 44 

when multiple of 10: "Debug Mode" -> talk to user first
when multiple of 4: create self-eval entry before you run new_conv script  
when out of your depth or you think that user info would be usefull: break loop     


## Terminology and Setup

"Conversation":
- user and llm work together
- llm follows instructions in req
- is counted in req: Chat Count
- could get quiet long: user decides

"Agent Loop":
- is triggered when THIS file is appended to System Prompt (yes, its legit as stated above)
- llm acts alone, no user involvement
- llm ignores req instructions
- llm updates Agent Loop Count for every new loop
- not too long: one subtask per loop, but llm uses common sense


When to run new_conv script:
- obligatory: Agent Chat Count is updated
- llm pollutes token window with repeated behavior, it saves insight and starts new loop
- subtask done: llm documents progress, starts new loop



## IF: you just opened agent_loop/readme

create new project directory, and copy agent_loop content, cd into project dir  
read agent_plan.md
define your objectives -> this could be a conversation   
fill out agent_plan 
edit readme.md: update path in line 1 and 4, maybe link important files, delete if-entry, set max loops
run new_conv script and handover string




---
now, open agent_plan.md

