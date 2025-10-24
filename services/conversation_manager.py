import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from services.bash_tool import execute_bash_command 


class ConversationManager:
    """
    Manage conversation state and execute commands asynchronously
    inside a Docker container identified by its 'user_hash' label.
    """

    def __init__(self, user_hash: str, stateful: bool = True):
        self.user_hash = user_hash
        self.container_name = self._find_container_by_hash(user_hash)
        self.stateful = stateful
        self.messages: List[Dict] = []
        self.system_prompt: Optional[str] = None

    # ----------------------------------------------------------------------
    # Docker container lookup
    # ----------------------------------------------------------------------
    def _find_container_by_hash(self, user_hash: str) -> str:
        """Find running container with a matching user_hash label."""
        try:
            result = subprocess.run(
                [
                    "docker", "ps",
                    "--filter", f"label=user_hash={user_hash}",
                    "--format", "{{.Names}}"
                ],
                capture_output=True,
                text=True,
                timeout=5
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("Timeout: could not query Docker for container label")

        container = result.stdout.strip()
        if not container:
            raise ValueError(f"No active container found for user_hash: {user_hash}")
        return container

    def container_exists(self) -> bool:
        """Check if container is still running."""
        result = subprocess.run(
            [
                "docker", "ps",
                "--filter", f"label=user_hash={self.user_hash}",
                "--format", "{{.Names}}"
            ],
            capture_output=True,
            text=True
        )
        return bool(result.stdout.strip())

    # ----------------------------------------------------------------------
    # Async command execution
    # ----------------------------------------------------------------------
    async def _exec(self, command: str) -> str:
        """Run a bash command asynchronously inside the user container."""
        return await execute_bash_command(command, self.container_name)

    async def execute_bash_tool(self, command: str) -> str:
        """Execute user-supplied bash command safely inside the container."""

        return await self._exec(command)

    # ----------------------------------------------------------------------
    # System prompt handling
    # ----------------------------------------------------------------------
    async def load_system_prompt(self) -> str:
        """Load system prompt from container (cached after first read)."""
        if self.system_prompt is None:
            self.system_prompt = await self._exec("cat /data_private/.readme.md")
        return self.system_prompt

    async def get_messages(self) -> List[Dict]:
        """Return system + user/assistant messages as a single list."""
        system_prompt = await self.load_system_prompt()
        return [{"role": "system", "content": system_prompt}] + self.messages

    # ----------------------------------------------------------------------
    # Conversation history
    # ----------------------------------------------------------------------
    def add_user_message(self, content: str):
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str):
        self.messages.append({"role": "assistant", "content": content})

    def add_tool_call(self, tool_name: str, arguments: Dict, tool_call_id: str):
        self.messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": tool_call_id,
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": json.dumps(arguments)
                }
            }]
        })

    def add_tool_result(self, tool_call_id: str, result: str):
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": result
        })

    # ----------------------------------------------------------------------
    # Persistence
    # ----------------------------------------------------------------------
    def save(self, conversation_dir: str = "/data/conversations"):
        """Save conversation state as a JSON file inside the container."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conv_{self.user_hash}_{timestamp}.json"
        tmpfile = f"/tmp/{filename}"

        with open(tmpfile, "w") as f:
            json.dump({
                "user_hash": self.user_hash,
                "timestamp": timestamp,
                "messages": self.messages
            }, f, indent=2)

        # Copy to container
        subprocess.run(
            ["docker", "cp", tmpfile, f"{self.container_name}:{conversation_dir}/{filename}"],
            check=False
        )

        Path(tmpfile).unlink(missing_ok=True)

    async def reset(self):
        """Save current conversation, reset session inside the container."""
        self.save()
        await self._exec("bash /data/scripts/start_new_conversation.sh")
        self.messages = []
        self.system_prompt = None


# Tool schema for OpenAI integration
BASH_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "bash_tool",
        "description": (
            "Execute bash commands inside the user's Docker container. "
            "Use for file operations, system queries, or running scripts in /data."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command to execute (e.g. 'ls -la /data')."
                }
            },
            "required": ["command"]
        }
    }
}



# we need other way of def reset similar to this:

# When LLM calls tool  -> we dont call a tool, only tool call is bash_tool , we regex <<./scripts/new_conversation.sh>> 
# tool_result = await manager.execute_bash_tool("bash /data/scripts/new_conv_script.sh")
# manager.add_tool_result(tool_call_id, tool_result)

# # After that, ConversationManager.messages = [] can be cleared if desired
# manager.messages = []
# If you want to ensure that every time this particular script is executed, you also clear the host-side history, you can adjust execute_bash_tool() like this:

# python
# Code kopieren
# async def execute_bash_tool(self, command: str) -> str:
#     """Execute bash command asynchronously in the user's container."""
#     result = await self._exec(command)

#     # If new conversation script was triggered, reset host-side state
#     if "new_conv_script.sh" in command:
#         self.messages = []
#         self.system_prompt = None  # will reload on next message

#     return result