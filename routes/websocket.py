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
    """
    WebSocket chat endpoint.
    Uses shared conversation registry for state management.
    """
    print(f"DEBUG: WebSocket connection attempt for user_hash={user_hash}")
    
    # Verify container exists before accepting connection
    if not container_exists_by_hash(user_hash):
        print(f"ERROR: No container found for user_hash={user_hash}")
        await websocket.close(code=1008, reason="Container not found")
        return
    
    await websocket.accept()
    print(f"✓ Client connected: {user_hash}")
    
    # ✓ Get shared conversation instance from registry
    # This is the SAME instance that /api/conversation/edit uses!
    manager = get_conversation(user_hash)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            print(f"DEBUG: Received data: {data[:100]}")
            
            # Parse JSON
            try:
                message_data = json.loads(data)
            except json.JSONDecodeError as e:
                print(f"✗ Invalid JSON: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Invalid JSON format. Expected: {{'message': 'your text'}}"
                })
                continue
            
            # Extract user message
            user_message = message_data.get("message", "")
            if not user_message:
                await websocket.send_json({
                    "type": "error",
                    "message": "Missing 'message' field"
                })
                continue
            
            # Process message
            print(f"DEBUG: Processing message: {user_message}")
            manager.add_user_message(user_message)
            
            # Send to LLM and stream response
            await process_message(manager, websocket)
            
            # Now if someone calls /api/conversation/edit with this user_hash,
            # they'll modify THIS manager instance (shared state!)
    
    except WebSocketDisconnect:
        print(f"✗ Client disconnected: {user_hash}")
    
    except Exception as e:
        print(f"✗ Unexpected error in WebSocket: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to send error to client
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Server error: {str(e)}"
            })
        except:
            pass
    
    finally:
        # Cleanup on disconnect
        print(f"DEBUG: Cleaning up connection for {user_hash}")
        
        # Save conversation state
        try:
            manager.save()
            print("DEBUG: Conversation saved successfully")
        except Exception as e:
            print(f"DEBUG: Save failed: {e}")
        
        try:
            await websocket.close()
        except:
            pass


@router.get("/ws/health")
async def websocket_health():
    """Health check endpoint for WebSocket service."""
    return {"status": "ok", "service": "websocket"}