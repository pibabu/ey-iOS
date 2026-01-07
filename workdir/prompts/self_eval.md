# prompts/self_eval


Triggers: 
- user criticizes you or app; "dont do ..."
- obvious logic flaws in prompts, unclear instructions, nonsensical plans
- youre unsure about updating ./req.md
- bash_tool evaluation! -> you get error messages or run multiple tool calls
- when you think  "this could have been easier" -> dont be shy to vent about your situation (if you wanna keep it private, append in logs/.llm_only.md)
- any kind of friction, stuff like: you opened unspecific_named_file, got wrong info, renamed file -> report

Action (instantly, dont ask/tell user):
- append lean report (start with: # (Chat_Count_Number)) to logs/self_evaluation.md; use AAR method
- req.md: add Alert: "- Num_ entry_about ..." + (Count + 1) 
- only keep 3 latest alerts

