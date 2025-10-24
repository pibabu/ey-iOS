from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pathlib import Path
import json
import subprocess
from services.llm import process_message
from services.conversation_manager import ConversationManager, BASH_TOOL_SCHEMA

app = FastAPI()


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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user_hash: str):
    # Validate by label, not name
    if not container_exists_by_hash(user_hash):
        await websocket.close(code=1008)
        return
    
    await websocket.accept()
    print(f"✓ Client connected: {user_hash}")

    #user_id = ""  # ##### <---
    cm = ConversationManager(user_hash, stateful=True)

    try:
        while True:
            
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")

            # Add user message using correct method
            cm.add_user_message(user_message)
            
            # Process message with LLM (streams response via websocket)
            await process_message(cm, websocket)
            
            # Note: process_message handles streaming,
            # actual response tracking would need to be added

    except WebSocketDisconnect:
        print("✗ Client disconnected")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        cm.save()
        try:
            await websocket.close()
        except:
            pass


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.post("/reset/{user_id}")
async def reset_conversation(user_id: str):

    try:
        cm = ConversationManager(user_id)
        cm.reset()
        return {"status": "success", "message": f"Conversation reset for user {user_id}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}