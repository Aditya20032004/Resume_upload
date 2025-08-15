"""
Day 14: Chat History Management Utilities
Handles chat session storage and management
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from models import ChatMessage, ChatSessionInfo, MessageRole


class ChatHistoryManager:
    """Manages chat sessions and message history"""
    
    def __init__(self):
        # In-memory storage for chat sessions
        self.sessions: Dict[str, ChatSessionInfo] = {}
    
    def create_session(self) -> str:
        """Create a new chat session and return session ID"""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        session_info = ChatSessionInfo(
            session_id=session_id,
            message_count=0,
            created_at=now,
            last_activity=now,
            messages=[]
        )
        
        self.sessions[session_id] = session_info
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ChatSessionInfo]:
        """Get session information by ID"""
        return self.sessions.get(session_id)
    
    def get_chat_history(self, session_id: str) -> List[ChatMessage]:
        """Get chat history for a session"""
        session = self.sessions.get(session_id)
        return session.messages if session else []
    
    def add_message(self, session_id: str, role: MessageRole, content: str) -> bool:
        """Add a message to chat history"""
        if session_id not in self.sessions:
            # Create session if it doesn't exist
            session_id = self.create_session()
        
        session = self.sessions[session_id]
        message = ChatMessage(role=role, content=content)
        
        session.messages.append(message)
        session.message_count = len(session.messages)
        session.last_activity = datetime.now()
        
        return True
    
    def add_user_message(self, session_id: str, content: str) -> bool:
        """Add a user message to chat history"""
        return self.add_message(session_id, MessageRole.USER, content)
    
    def add_assistant_message(self, session_id: str, content: str) -> bool:
        """Add an assistant message to chat history"""
        return self.add_message(session_id, MessageRole.ASSISTANT, content)
    
    def clear_session(self, session_id: str) -> bool:
        """Clear chat history for a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_recent_messages(self, session_id: str, limit: int = 10) -> List[ChatMessage]:
        """Get recent messages from a session"""
        messages = self.get_chat_history(session_id)
        return messages[-limit:] if messages else []
    
    def get_session_stats(self) -> dict:
        """Get statistics about all sessions"""
        total_sessions = len(self.sessions)
        total_messages = sum(session.message_count for session in self.sessions.values())
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "active_sessions": [sid for sid, session in self.sessions.items() 
                              if session.message_count > 0]
        }


# Global chat history manager
chat_manager = ChatHistoryManager()
