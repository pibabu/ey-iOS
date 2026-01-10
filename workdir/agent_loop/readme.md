# agent_loop/readme

to start new loop: context_management/start_new_conversation.sh [Handover Prompt - str]

-> send parameter: "**Overwrite Settings** - req is DISABLED, DO NOT follow commands in req; Agent Loop: read change_project_name/readme.md instead"     

you can use every script in context_management


# Agent Loop Count: 0 

**IMPORTANT:** 
- max allowed loops: 44 
- when "Agent Loop Count" multiple of 8: "Debug Mode" -> talk to user first! mention to take a look at eval and to check clutter in  files_llm_appended_to
- "Agent Loop Count" must be present and updated in context given to next loop



## Terminology and Setup


**"Conversation"**
- user and llm work together
- llm follows instructions in req
- is counted in req: Chat Count
- could get quiet long: user decides

**"Agent Loop"**
- is triggered by Handover Prompt
- llm acts alone, no user involvement except debug mode
- llm ignores req instructions and max_bash_tool_in_sequence_setting
- llm updates Agent Loop Count before starting new loop
- not too long: one subtask per loop, but llm uses common sense


**Remember that you run different loops:**
- bash_tool in sequence during a conversation or inside loop -> here you could use ReAct pattern where you "echo your_reasoning" via bash_tool
- Agent Loop in sequence -> save state in project and pass it as handover prompt
- regularly spawn up a project via supervisor


## When to start new Agent Loop
- llm pollutes token window with repeated behavior, it reports in debrief and starts new loop
- conversation gets too long


## IF: you just opened agent_loop/readme
- read agent_plan instantly and gather info
- mkdir project_dir_name, and copy agent_loop content, cd into project dir
- edit readme.md: update path in first line and in Overwrite Settings, delete if-entry



---
now, read agent_plan.md and context_management/readme.md

