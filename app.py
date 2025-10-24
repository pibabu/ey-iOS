from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pathlib import Path
import json
import subprocess
from services.llm import process_message
from services.conversation_manager import ConversationManager, BASH_TOOL_SCHEMA
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domains: ["https://yourdomain.com"]
    allow_credentials=True,
    allow_methods=["*"],  # Or specify: ["GET", "POST", "PUT", "DELETE"]
    allow_headers=["*"],  # Or specify headers you need
)


@app.get("/")
async def serve_frontend():
    html_file = Path("index.html")

    if html_file.exists():
        return HTMLResponse(content=html_file.read_text())
    else:
        return HTMLResponse(
            content="<h1>Error: index.html not found</h1>", status_code=404
        )


def container_exists_by_hash(user_hash: str) -> bool:
    """Check if container with user_hash label exists."""
    result = subprocess.run(
        ["docker", "ps", "--filter", f"label=user_hash={user_hash}", 
         "--format", "{{.Names}}"],
        capture_output=True,
        text=True
    )
    return bool(result.stdout.strip())


@app.websocket("/ws/{user_hash}")
async def websocket_endpoint(
    websocket: WebSocket, 
    user_hash: str  # From URL path
):
    print(f"DEBUG: WebSocket connection attempt for user_hash={user_hash}")
    
    if not container_exists_by_hash(user_hash):
        print(f"ERROR: No container found for user_hash={user_hash}")
        await websocket.close(code=1008, reason="Container not found")
        return
    
    
    await websocket.accept()
    print(f"✓ Client connected: {user_hash}")

    #user_id = ""  # ##### <---
    #cm = ConversationManager(user_hash, stateful=True)
    manager = ConversationManager(user_hash=user_hash)

    try:
        while True:
            
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")

            # Add user message using correct method
            manager.add_user_message(user_message)
            
            # Process message with LLM (streams response via websocket)
            await process_message(manager, websocket)
            
            # Note: process_message handles streaming,
            # actual response tracking would need to be added

    except WebSocketDisconnect:
        print("✗ Client disconnected")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        manager.save()
        try:
            await websocket.close()
        except:
            pass


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.post("/reset/{user_hash}")   ###change ??
async def reset_conversation(user_hash: str):

    try:
        manager = ConversationManager(user_hash)
        manager.reset()
        return {"status": "success", "message": f"Conversation reset for user {user_hash}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}