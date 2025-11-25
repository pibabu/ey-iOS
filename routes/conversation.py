from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from services.conversation_registry import get_conversation 

router = APIRouter(prefix="/api/conversation", tags=["conversation"])


# ============================================
# REQUEST MODELS
# ============================================
class MessageEdit(BaseModel):
    role: Literal["user", "assistant", "tool"]
    content: str


class ConversationEditRequest(BaseModel):
    user_hash: str
    action: Literal["clear", "replace_last", "inject", "remove_last"]
    count: Optional[int] = Field(1, ge=1, le=20)
    new_messages: Optional[List[MessageEdit]] = None
    system_prompt_append: Optional[str] = None 


# ============================================
# ENDPOINTS
# ============================================
@router.post("/edit")
async def edit_conversation(request: ConversationEditRequest):
    """
    Modify conversation history for active session.
    
    Actions:
    - clear: Wipe all messages (optionally set system_prompt_append)
    - replace_last: Replace last N messages with new ones
    - inject: Append new messages
    - remove_last: Delete last N messages
    """
    try:
        cm = get_conversation(request.user_hash)
        
        if request.action == "clear":
            cm.messages.clear()
            
            if request.system_prompt_append is not None:
                cm.set_system_prompt_append(request.system_prompt_append)
            
            return {
                "status": "success",
                "action": "cleared",
                "message_count": 0,
                "system_prompt_append_set": request.system_prompt_append is not None
            }
        
        elif request.action == "replace_last":
            if not request.new_messages:
                raise HTTPException(400, "new_messages required")
            
            to_remove = min(request.count, len(cm.messages))
            cm.messages = cm.messages[:-to_remove] if to_remove > 0 else cm.messages
            
            for msg in request.new_messages:
                cm.messages.append({"role": msg.role, "content": msg.content})
            
            return {
                "status": "success",
                "action": "replaced",
                "removed": to_remove,
                "added": len(request.new_messages),
                "total": len(cm.messages)
            }
        
        elif request.action == "inject":
            if not request.new_messages:
                raise HTTPException(400, "new_messages required")
            
            for msg in request.new_messages:
                cm.messages.append({"role": msg.role, "content": msg.content})
            
            return {
                "status": "success",
                "action": "injected",
                "added": len(request.new_messages),
                "total": len(cm.messages)
            }
        
        elif request.action == "remove_last":
            to_remove = min(request.count, len(cm.messages))
            cm.messages = cm.messages[:-to_remove] if to_remove > 0 else cm.messages
            
            return {
                "status": "success",
                "action": "removed",
                "removed": to_remove,
                "total": len(cm.messages)
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Edit failed: {str(e)}")


@router.get("/status")
async def get_status(user_hash: str):
    """Get current conversation status (message count, container info)."""
    try:
        cm = get_conversation(user_hash)
        return {
            "user_hash": user_hash,
            "container_name": cm.container_name,
            "message_count": len(cm.messages),
            "has_system_prompt": cm.system_prompt is not None,
            "system_prompt_append": cm.system_prompt_append
        }
    except Exception as e:
        raise HTTPException(500, f"Status check failed: {str(e)}")


@router.post("/export")
async def export_conversation(request: dict):
    """Export full conversation data."""
    user_hash = request.get("user_hash")
    if not user_hash:
        raise HTTPException(400, "user_hash required")
    
    cm = get_conversation(user_hash)
    return cm.get_conversation_data()