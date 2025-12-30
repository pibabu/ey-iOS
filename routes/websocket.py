from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import subprocess
from services.llm_chat import process_message
from services.conversation_registry import get_conversation, remove_conversation

router = APIRouter()


def container_exists_by_hash(user_hash: str) -> bool:
    """Check if container with user_hash label exists."""
    result = subprocess.run(
        ["docker", "ps", "--filter", f"label=user_hash={user_hash}", 
         "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
        timeout=5
    )
    return bool(result.stdout.strip())


@router.websocket("/ws/{user_hash}")
async def websocket_endpoint(websocket: WebSocket, user_hash: str):

    print(f"DEBUG: WebSocket connection attempt for user_hash={user_hash}")
    
    # Verify container exists
    if not container_exists_by_hash(user_hash):
        print(f"ERROR: No container found for user_hash={user_hash}")
        await websocket.close(code=1008, reason="Container not found")
        return
    
    await websocket.accept()
    print(f"✓ Client connected: {user_hash}")
    

    manager = get_conversation(user_hash)
    print(f"DEBUG: Loaded manager with {len(manager.messages)} existing messages")
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            print(f"DEBUG: Received: {data[:100]}")
            
            # Parse JSON
            try:
                message_data = json.loads(data)
            except json.JSONDecodeError as e:
                print(f"✗ Invalid JSON: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON. Expected: {'message': 'text'}"
                })
                continue
            
            # Extract message
            user_message = message_data.get("message", "")
            if not user_message:
                await websocket.send_json({
                    "type": "error",
                    "message": "Missing 'message' field"
                })
                continue
            
            # Add to conversation (modifies Python list in memory)
            print(f"DEBUG: Processing: {user_message}")
            manager.add_user_message(user_message)
            
            # Process with LLM (will add responses to manager.messages)
            await process_message(manager, websocket)

    
    except WebSocketDisconnect:
        print(f"✗ Client disconnected: {user_hash}")
    
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Server error: {str(e)}"
            })
        except:
            pass
    
    finally:
        # Close connection
        print(f"DEBUG: Closing connection for {user_hash}")
        try:
            await websocket.close()
        except:
            pass
        
@router.get("/ws/health")
async def websocket_health():
    """Health check endpoint for WebSocket service."""
    return {"status": "ok", "service": "websocket"}