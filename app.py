import asyncio
import os
import json
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from openai import AsyncOpenAI
import docker
from docker.errors import DockerException, NotFound

load_dotenv()

app = FastAPI()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize Docker client
try:
    docker_client = docker.from_env()
    print("✓ Docker client initialized")
except DockerException as e:
    print(f"❌ Docker connection failed: {e}")
    docker_client = None


# ═══════════════════════════════════════════════════════
# DOCKER CONTAINER MANAGEMENT
# ═══════════════════════════════════════════════════════


def ensure_shared_volume():
    """
    Creates the shared volume if it doesn't exist.
    This volume is mounted to ALL user containers for announcements.
    """
    try:
        docker_client.volumes.get("shared_volume")
        print("✓ Shared volume exists")
    except NotFound:
        docker_client.volumes.create("shared_volume")
        print("✓ Created shared_volume")


def create_user_volume(username: str) -> str:
    """
    Creates a private volume for a specific user.
    Volume name pattern: user_{username}_volume

    Returns: volume name
    """
    volume_name = f"user_{username}_volume"
    try:
        docker_client.volumes.get(volume_name)
        print(f"✓ Volume {volume_name} already exists")
    except NotFound:
        docker_client.volumes.create(volume_name)
        print(f"✓ Created {volume_name}")
    return volume_name


def register_user_in_shared_volume(username: str, metadata: dict):
    """
    Adds user to registry file in shared volume.
    We do this by running a temporary container that writes to the volume.
    """
    registry_entry = {
        "username": username,
        "registered_at": datetime.now().isoformat(),
        "metadata": metadata,
    }

    # Use a temporary Alpine container to write to the volume
    command = f"echo '{json.dumps(registry_entry)}' >> /shared/registry_users.jsonl"

    try:
        docker_client.containers.run(
            "alpine:latest",
            command=f'sh -c "{command}"',
            volumes={"shared_volume": {"bind": "/shared", "mode": "rw"}},
            remove=True,
        )
        print(f"✓ Registered {username} in shared volume")
    except Exception as e:
        print(f"❌ Failed to register user: {e}")


def start_user_container(username: str, metadata: dict) -> Optional[str]:
    """
    Starts a user's container with:
    - Private volume mounted to /home/user/
    - Shared volume mounted to /shared/
    - Container name: user_{username}_container
    - Labels with user metadata

    Returns: container ID or None if failed
    """
    if not docker_client:
        print("❌ Docker client not available")
        return None

    container_name = f"user_{username}_container"

    # Check if container already exists
    try:
        existing = docker_client.containers.get(container_name)
        print(
            f"⚠ Container {container_name} already exists (status: {existing.status})"
        )
        if existing.status != "running":
            existing.start()
            print(f"✓ Started existing container")
        return existing.id
    except NotFound:
        pass  # Container doesn't exist, we'll create it

    # Ensure volumes exist
    ensure_shared_volume()
    user_volume = create_user_volume(username)

    # Register user in shared volume
    register_user_in_shared_volume(username, metadata)

    # Start the container
    try:
        container = docker_client.containers.run(
            "ubuntu:22.04",
            name=container_name,
            detach=True,
            tty=True,  # Keep container running
            stdin_open=True,
            volumes={
                user_volume: {"bind": "/home/user", "mode": "rw"},
                "shared_volume": {
                    "bind": "/shared",
                    "mode": "ro",
                },  # Read-only for users
            },
            labels={
                "user": username,
                "name": metadata.get("name", ""),
                "age": str(metadata.get("age", "")),
                "job": metadata.get("job", ""),
                "interests": metadata.get("interests", ""),
            },
            command="tail -f /dev/null",  # Keep container alive
        )

        print(f"✓ Started container {container_name} (ID: {container.short_id})")

        # Create README in user's home directory
        exec_result = container.exec_run(
            f"sh -c 'echo \"Welcome {metadata.get('name', username)}!\" > /home/user/README.md'"
        )
        print(f"✓ Created README.md for {username}")

        return container.id

    except Exception as e:
        print(f"❌ Failed to start container: {e}")
        return None


def get_container_info(username: str) -> Optional[dict]:
    """Get information about a user's container"""
    try:
        container = docker_client.containers.get(f"user_{username}_container")
        return {
            "id": container.short_id,
            "status": container.status,
            "name": container.name,
            "labels": container.labels,
        }
    except NotFound:
        return None
    except Exception as e:
        print(f"❌ Error getting container info: {e}")
        return None


# ═══════════════════════════════════════════════════════
# AI SERVICE WITH TOOL CALLING
# ═══════════════════════════════════════════════════════

# Tool definition for OpenAI function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "start_container",
            "description": "Start a Docker container for a user with their personal workspace",
            "parameters": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Username (lowercase, no spaces)",
                    },
                    "name": {"type": "string", "description": "User's full name"},
                    "age": {"type": "integer", "description": "User's age"},
                    "job": {"type": "string", "description": "User's job/occupation"},
                    "interests": {
                        "type": "string",
                        "description": "User's interests (comma-separated)",
                    },
                },
                "required": ["username", "name"],
            },
        },
    }
]


async def handle_tool_call(tool_call, websocket):
    """Execute tool calls from the LLM"""
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    print(f"🔧 Tool call: {function_name}")
    print(f"📋 Arguments: {arguments}")

    if function_name == "start_container":
        username = arguments.get("username")
        metadata = {
            "name": arguments.get("name"),
            "age": arguments.get("age"),
            "job": arguments.get("job", ""),
            "interests": arguments.get("interests", ""),
        }

        # Start the container
        container_id = start_user_container(username, metadata)

        if container_id:
            result = {
                "success": True,
                "container_id": container_id,
                "message": f"Container started for {username}",
            }
        else:
            result = {"success": False, "message": "Failed to start container"}

        # Send status update to frontend
        await websocket.send_json({"type": "container_status", "data": result})

        return json.dumps(result)

    return json.dumps({"error": "Unknown function"})


async def process_message(user_message: str, websocket):
    """Process message with AI and handle tool calls"""

    await websocket.send_json({"type": "start"})

    # Conversation history (in production, maintain this per session)
    messages = [
        {
            "role": "system",
            "content": """You are a helpful assistant that manages user workspaces. 
When a user first connects, ask for their:
- Name
- Age
- Job/occupation
- Interests

Once you have this info, use the start_container function to set up their workspace.""",
        },
        {"role": "user", "content": user_message},
    ]

    try:
        # Initial API call with tools
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            stream=False,  # First call non-streaming to check for tool calls
        )

        assistant_message = response.choices[0].message

        # Handle tool calls
        if assistant_message.tool_calls:
            print(f"🔧 Detected {len(assistant_message.tool_calls)} tool call(s)")

            # Add assistant message to history
            messages.append(assistant_message)

            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                function_response = await handle_tool_call(tool_call, websocket)

                # Add tool response to messages
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": function_response,
                    }
                )

            # Get final response after tool execution (streaming)
            stream = await client.chat.completions.create(
                model="gpt-4o-mini", messages=messages, stream=True
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    await websocket.send_json(
                        {"type": "token", "content": chunk.choices[0].delta.content}
                    )

        else:
            # No tool calls, just stream the response
            content = assistant_message.content
            if content:
                await websocket.send_json({"type": "token", "content": content})

        await websocket.send_json({"type": "end"})

    except Exception as e:
        await websocket.send_json(
            {"type": "error", "message": f"AI service error: {str(e)}"}
        )
        print(f"❌ OpenAI API Error: {e}")


# ═══════════════════════════════════════════════════════
# FASTAPI ROUTES
# ═══════════════════════════════════════════════════════


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    print("✓ Client connected")

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            print(f"📩 Received: {user_message}")

            await process_message(user_message, websocket)

    except WebSocketDisconnect:
        print("✗ Client disconnected")
    except Exception as e:
        print(f"❌ Error: {e}")
        await websocket.close()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    docker_status = "connected" if docker_client else "disconnected"
    return {"status": "ok", "docker": docker_status}


@app.get("/containers")
async def list_containers():
    """List all user containers (debug endpoint)"""
    if not docker_client:
        return {"error": "Docker not available"}

    containers = docker_client.containers.list(all=True, filters={"name": "user_"})

    return {
        "containers": [
            {"name": c.name, "status": c.status, "id": c.short_id, "labels": c.labels}
            for c in containers
        ]
    }


@app.get("/volumes")
async def list_volumes():
    """List all volumes (debug endpoint)"""
    if not docker_client:
        return {"error": "Docker not available"}

    volumes = docker_client.volumes.list()
    return {"volumes": [v.name for v in volumes]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=80)
