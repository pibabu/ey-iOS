import asyncio

async def execute_bash_command(command: str, container_name: str) -> str:
    """Execute a bash command asynchronously inside a Docker container."""
    try:
        proc = await asyncio.create_subprocess_shell(
            f"docker exec {container_name} bash -c '{command}'",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        output = (stdout + stderr).decode().strip()
        return output or "(no output)"
    except Exception as e:
        return f"Error executing command: {e}"
    
