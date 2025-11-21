"""
Shared registry for ConversationManager instances.
Ensures WebSocket and API endpoints use the SAME conversation object.
"""
from typing import Dict
from services.conversation_manager import ConversationManager

_active_conversations: Dict[str, ConversationManager] = {}


def get_conversation(user_hash: str) -> ConversationManager:
   
    if user_hash not in _active_conversations:
        _active_conversations[user_hash] = ConversationManager(user_hash)
    
    return _active_conversations[user_hash]


def remove_conversation(user_hash: str) -> bool:
    """
    Remove conversation from registry (cleanup).
    Returns True if removed, False if didn't exist.
    """
    if user_hash in _active_conversations:
        del _active_conversations[user_hash]
        return True
    return False


def list_active_conversations() -> list[str]:
    """Return list of all active user_hashes (for debugging)."""
    return list(_active_conversations.keys())