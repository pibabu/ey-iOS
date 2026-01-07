# agent_loop/readme

script to call: context_management/start_new_conversation.sh [str]

-> send as parameter: "**Overwrite Settings** - req is DISABLED, read current_project_name/readme.md instead"     

## Agent Loop Count: 0 

IMPORTANT - max allowed loops: 44 

when multiple of 8: "Debug Mode" -> talk to user first! mention to take a look at self_eval and to check clutter in  files_llm_appended_to


## Terminology and Setup

"Conversation":
- user and llm work together
- llm follows instructions in req
- is counted in req: Chat Count
- could get quiet long: user decides

"Agent Loop":
- is triggered by Handover Prompt
- llm acts alone, no user involvement except debug mode
- llm ignores req instructions and max_bash_tool_in_sequence_setting
- llm updates Agent Loop Count before starting new loop!
- not too long: one subtask per loop, but llm uses common sense
- dynamic loop: llm can redefine agent_plan as well as any other file in work dir


## When to start new loop
- llm pollutes token window with repeated behavior, it reports in debrief and starts new loop
- subtask done: llm appends debrief, starts new loop


## Obligatory before new loop
- Agent Chat Count is updated and max_loop is set!
- Right before running script, go deep into yourself and append "Loop_Count_Number Debrief: your_lean_job_report_and reason_why_you_run_new_loop" to self_eval.md
- Make sure to send right files as parameter


## IF: you just opened agent_loop/readme
- read agent_plan instantly and gather info
- mkdir project_dir_name, and copy agent_loop content, cd into project dir
- edit readme.md: update path in first line and in Overwrite Settings, delete if-entry



---
now, open agent_plan.md

