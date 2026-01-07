# agent_plan

## obligatory

- define the maximal loop count (with users confirmation) 
- integrate steps that break loop regularly



# planing phase -> this could be a longer conversation

create simple to-do list or use project management frameworks/project initiation techniques for complex tasks - but remember: get shit done



## Agent Loop
Use your vast internal knowledge about prompting techniques to find the right strategy for task. You might delete self_eval in readme.    
Patterns you could use:


### Plan-and-Execute:
1. Analyze the user's request thoroughly, define goals and set max_loop_count 
2. Create a detailed plan with numbered substeps and map them to loop_count
3. Execute each step sequentially, map your progress
4. Check off completed steps and adapt the plan if needed
5. Monitor loop_number vs task_progress


### Self-Ask:
- Look at the main question
- Ask yourself: "What sub-questions must I answer first?" "How many loops do I need?"
- map questions to loop_count
- run loop, monitor progress


### Few Shot Examples
- together you create the best examples for task or workflow


### Tree of Thoughts
- explore and evaluate multiple reasoning path -> save them in different files; they become optional context in next loops
- save report/rating of each loop in file; link file in readme

### Multi-Agent Patterns
- 








