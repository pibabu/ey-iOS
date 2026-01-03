# agent_loop/readme

script to call: context_management/start_new_conversation.sh [str]

-> send as parameter: "**Overwrite Settings** - req is DISABLED, read current_project_name/readme.md instead"     

## Agent Loop Count: 0 

IMPORTANT - max allowed loops: 44 

when multiple of 10: "Debug Mode" -> talk to user first, mention to take a look at self_eval   

when out of your depth or you think that user info would be usefull: break loop     


## Terminology and Setup

"Conversation":
- user and llm work together
- llm follows instructions in req
- is counted in req: Chat Count
- could get quiet long: user decides

"Agent Loop":
- is triggered by Overwrite Settings Prompt
- llm acts alone, no user involvement
- llm ignores req instructions
- llm updates Agent Loop Count before starting new loop!
- not too long: one subtask per loop, but llm uses common sense
- dynamic loop: llm can redefine agent_plan as well as any other file in work dir


## When to start new loop
- llm pollutes token window with repeated behavior, it appends insight to agent_plan and starts new loop
- subtask done: llm documents progress, starts new loop


## Obligatory before new loop
- Agent Chat Count is updated!
- Right before starting new conv: go deep into youself, analyse overall setup and append lean report to self_eval.md
- Make sure to send right project/readme as parameter


## IF: you just opened agent_loop/readme
- make sure that llm and user are on same page, get project name and goals
- create new project directory, and copy agent_loop content, cd into project dir
- read agent_plan.md
- define your objectives -> this could be a conversation
- fill out agent_plan
- edit readme.md: update path in line 1 and 5, delete if-entry, set max loops
- start loop after user confirmation




---
now, open agent_plan.md

