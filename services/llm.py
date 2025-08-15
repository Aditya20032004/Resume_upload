"""
Day 14: Large Language Model Service
Handles text generation using Google Gemini AI
"""

import google.generativeai as genai
from typing import List, Optional

from config import config, logger
from models import LLMRequest, LLMResponse, ChatMessage, ErrorType, MessageRole


class LLMService:
    """LLM service using Google Gemini AI"""
    
    def __init__(self):
        self.api_key = config.GEMINI_API_KEY
        self.model_name = "gemini-1.5-flash"
        self.timeout = config.LLM_TIMEOUT
        self._setup_client()
    
    def _setup_client(self) -> None:
        """Setup Gemini AI client"""
        if not self.api_key or self.api_key == 'your_gemini_api_key_here':
            logger.warning("Gemini API key not configured")
            self.client = None
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model_name)
            logger.info("Gemini AI client configured successfully")
        except Exception as e:
            logger.error(f"Failed to setup Gemini AI client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if LLM service is available"""
        return self.client is not None and self.api_key is not None
    
    def generate_response(self, request: LLMRequest, chat_history: List[ChatMessage] = None) -> LLMResponse:
        """
        Generate response using LLM
        
        Args:
            request: LLM request with text and parameters
            chat_history: Optional chat history for context
            
        Returns:
            LLMResponse with generated text
        """
        if not self.is_available():
            fallback = self._generate_contextual_fallback(request.text)
            return LLMResponse(
                success=False,
                error="LLM service not available - API key not configured",
                error_type=ErrorType.CONFIG_ERROR,
                fallback_response=fallback,
                query=request.text,
                session_id=request.session_id
            )
        
        try:
            # Prepare conversation context
            conversation_context = self._prepare_context(request, chat_history)
            
            # Generate response
            response = self._generate_llm_response(conversation_context)
            
            return LLMResponse(
                success=True,
                response=response,
                query=request.text,
                model=self.model_name,
                session_id=request.session_id
            )
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            fallback = self._generate_contextual_fallback(request.text)
            
            return LLMResponse(
                success=False,
                error=f"LLM generation failed: {str(e)}",
                error_type=ErrorType.LLM_ERROR,
                fallback_response=fallback,
                query=request.text,
                session_id=request.session_id
            )
    
    def _prepare_context(self, request: LLMRequest, chat_history: List[ChatMessage] = None) -> str:
        """Prepare conversation context with history"""
        context_parts = []
        
        # Add system prompt
        system_prompt = (
            "You are a helpful AI voice assistant. Provide clear, concise, and helpful responses. "
            "Keep your responses conversational and engaging, suitable for voice interaction."
        )
        context_parts.append(f"System: {system_prompt}")
        
        # Add chat history if available and requested
        if request.include_history and chat_history:
            context_parts.append("\nConversation History:")
            for message in chat_history[-10:]:  # Last 10 messages for context
                role = "User" if message.role == MessageRole.USER else "Assistant"
                context_parts.append(f"{role}: {message.content}")
        
        # Add current user message
        context_parts.append(f"\nUser: {request.text}")
        context_parts.append("Assistant:")
        
        return "\n".join(context_parts)
    
    def _generate_llm_response(self, context: str) -> str:
        """Generate response using Gemini AI"""
        try:
            logger.info("Generating LLM response with Gemini...")
            response = self.client.generate_content(context)
            
            if not response.text:
                raise Exception("Empty response from LLM")
            
            logger.info(f"LLM response generated: {response.text[:100]}...")
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise
    
    def _generate_contextual_fallback(self, user_text: str) -> str:
        """Generate contextual fallback response when LLM fails"""
        if not user_text:
            return "I didn't catch that. Could you please repeat your message?"
        
        user_lower = user_text.lower()
        
        # Context-aware fallback responses
        if any(word in user_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return "Hello! I'm having some technical difficulties with my AI brain, but I'm here to help as best I can."
        elif any(word in user_lower for word in ['how are you', 'how do you do']):
            return "I'm experiencing some technical issues right now, but thank you for asking! How can I help you?"
        elif any(word in user_lower for word in ['thank', 'thanks']):
            return "You're very welcome! Though I should mention I'm having some connectivity issues at the moment."
        elif any(word in user_lower for word in ['bye', 'goodbye', 'see you', 'farewell']):
            return "Goodbye! Sorry for any technical difficulties during our conversation. Hope to chat again soon!"
        elif any(word in user_lower for word in ['help', 'support', 'assist']):
            return "I'd love to help you! I'm currently experiencing some technical difficulties, but I'll do my best to assist."
        elif any(word in user_lower for word in ['what', 'how', 'why', 'when', 'where', 'who']):
            return "That's a great question! Unfortunately, I'm having trouble accessing my full knowledge base right now, but please try asking again in a moment."
        else:
            preview = user_text[:50] + "..." if len(user_text) > 50 else user_text
            return f"I heard you mention something about '{preview}'. I'm experiencing some technical difficulties, but I'm trying to help as best I can."
    
    def health_check(self) -> dict:
        """Check LLM service health"""
        return {
            "service": "Google Gemini",
            "model": self.model_name,
            "available": self.is_available(),
            "api_key_configured": bool(self.api_key and self.api_key != 'your_gemini_api_key_here'),
            "timeout": self.timeout
        }


# Global LLM service instance
llm_service = LLMService()
