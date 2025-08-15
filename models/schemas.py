"""
Day 14: Pydantic Models for Request/Response Schemas
Defines data models for API endpoints with validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ErrorType(str, Enum):
    """Enumeration of possible error types"""
    STT_ERROR = "stt_error"
    LLM_ERROR = "llm_error"
    TTS_ERROR = "tts_error"
    API_ERROR = "api_error"
    NETWORK_ERROR = "network_error"
    TIMEOUT_ERROR = "timeout_error"
    GENERAL_ERROR = "general_error"
    CONFIG_ERROR = "config_error"
    INPUT_ERROR = "input_error"


class MessageRole(str, Enum):
    """Chat message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Individual chat message model"""
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)


class TTSRequest(BaseModel):
    """Text-to-Speech request model"""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to convert to speech")
    voice_id: Optional[str] = Field(default="en-US-AriaNeural", description="Voice ID for TTS")
    speed: Optional[int] = Field(default=95, ge=50, le=200, description="Speech speed (50-200)")
    pitch: Optional[int] = Field(default=45, ge=0, le=100, description="Speech pitch (0-100)")

    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty or whitespace only')
        return v.strip()


class TTSResponse(BaseModel):
    """Text-to-Speech response model"""
    success: bool
    audio_url: Optional[str] = None
    error: Optional[str] = None
    error_type: Optional[ErrorType] = None
    emergency_fallback: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class LLMRequest(BaseModel):
    """LLM query request model"""
    text: str = Field(..., min_length=1, max_length=10000, description="Text to send to LLM")
    session_id: Optional[str] = Field(default=None, description="Session ID for chat history")
    model: Optional[str] = Field(default="gemini-1.5-flash", description="LLM model to use")
    include_history: Optional[bool] = Field(default=True, description="Include chat history in context")

    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty or whitespace only')
        return v.strip()


class LLMResponse(BaseModel):
    """LLM query response model"""
    success: bool = True
    response: Optional[str] = None
    query: Optional[str] = None
    model: Optional[str] = None
    session_id: Optional[str] = None
    error: Optional[str] = None
    error_type: Optional[ErrorType] = None
    fallback_response: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    day: int = 14
    challenge: str = "30 Days of Voice Agents"


class TranscriptionRequest(BaseModel):
    """Audio transcription request model"""
    audio_format: Optional[str] = Field(default="webm", description="Audio file format")
    language: Optional[str] = Field(default="en", description="Language code for transcription")
    model: Optional[str] = Field(default="best", description="Transcription model to use")


class TranscriptionResponse(BaseModel):
    """Audio transcription response model"""
    success: bool
    transcription: Optional[str] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    language: Optional[str] = None
    error: Optional[str] = None
    error_type: Optional[ErrorType] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class VoiceQueryRequest(BaseModel):
    """Complete voice query request model (audio + optional parameters)"""
    session_id: Optional[str] = Field(default=None, description="Session ID for chat continuity")
    language: Optional[str] = Field(default="en", description="Language for processing")
    voice_id: Optional[str] = Field(default="en-US-AriaNeural", description="Voice for TTS response")
    include_history: Optional[bool] = Field(default=True, description="Include chat history")


class VoiceQueryResponse(BaseModel):
    """Complete voice query response model"""
    success: bool
    transcription: Optional[str] = None
    llm_response: Optional[str] = None
    audio_url: Optional[str] = None
    confidence: Optional[float] = None
    chat_history: Optional[List[ChatMessage]] = None
    session_id: Optional[str] = None
    message_count: Optional[int] = None
    error: Optional[str] = None
    error_type: Optional[ErrorType] = None
    fallback_used: Optional[bool] = False
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str = "healthy"
    version: str = "1.0.0"
    day: int = 14
    services: Dict[str, bool] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Standard error response model"""
    success: bool = False
    error: str
    error_type: ErrorType
    details: Optional[Dict[str, Any]] = None
    fallback_action: Optional[str] = None
    retry_after: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatSessionInfo(BaseModel):
    """Chat session information model"""
    session_id: str
    message_count: int
    created_at: datetime
    last_activity: datetime
    messages: List[ChatMessage]
