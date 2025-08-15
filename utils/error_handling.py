"""
Day 14: Error Handling Utilities
Centralized error handling and fallback responses
"""

from typing import Dict, Any, Optional
from models import ErrorResponse, ErrorType


class ErrorHandler:
    """Centralized error handling"""
    
    @staticmethod
    def get_fallback_response(error_type: ErrorType, context: str = "") -> str:
        """Get appropriate fallback messages based on error type"""
        fallback_messages = {
            ErrorType.STT_ERROR: "I'm having trouble hearing you right now. Please try speaking again clearly.",
            ErrorType.LLM_ERROR: "I'm having trouble connecting to my knowledge base. Let me try to help you anyway.",
            ErrorType.TTS_ERROR: "I can understand you, but I'm having trouble speaking right now.",
            ErrorType.API_ERROR: "I'm experiencing technical difficulties. Please try again later.",
            ErrorType.NETWORK_ERROR: "I'm having trouble connecting right now. Please check your connection and try again.",
            ErrorType.TIMEOUT_ERROR: "The request is taking too long. Please try again with a shorter message.",
            ErrorType.GENERAL_ERROR: "Something went wrong. Please try again.",
            ErrorType.CONFIG_ERROR: "Service configuration issue. Please contact support.",
            ErrorType.INPUT_ERROR: "There seems to be an issue with your input. Please check and try again."
        }
        return fallback_messages.get(error_type, fallback_messages[ErrorType.GENERAL_ERROR])
    
    @staticmethod
    def create_error_response(
        error_message: str, 
        error_type: ErrorType = ErrorType.GENERAL_ERROR,
        details: Optional[Dict[str, Any]] = None,
        fallback_action: Optional[str] = None,
        retry_after: Optional[int] = None
    ) -> ErrorResponse:
        """Create standardized error response"""
        return ErrorResponse(
            error=error_message,
            error_type=error_type,
            details=details,
            fallback_action=fallback_action,
            retry_after=retry_after
        )
    
    @staticmethod
    def log_error(logger, error: Exception, context: str = ""):
        """Log error with context"""
        error_msg = f"{context}: {str(error)}" if context else str(error)
        logger.error(error_msg, exc_info=True)


class ValidationUtils:
    """Input validation utilities"""
    
    @staticmethod
    def validate_audio_file(file) -> Optional[str]:
        """Validate uploaded audio file"""
        if not file:
            return "No audio file provided"
        
        if file.filename == '':
            return "No file selected"
        
        # Check file size (16MB limit)
        if hasattr(file, 'content_length') and file.content_length:
            if file.content_length > 16 * 1024 * 1024:
                return "File too large (max 16MB)"
        
        # Check file extension
        allowed_extensions = {'.webm', '.wav', '.mp3', '.m4a', '.ogg'}
        if file.filename:
            file_ext = '.' + file.filename.rsplit('.', 1)[-1].lower()
            if file_ext not in allowed_extensions:
                return f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
        
        return None
    
    @staticmethod
    def validate_text_input(text: str, max_length: int = 10000) -> Optional[str]:
        """Validate text input"""
        if not text:
            return "Text cannot be empty"
        
        text = text.strip()
        if not text:
            return "Text cannot be empty or whitespace only"
        
        if len(text) > max_length:
            return f"Text too long (max {max_length} characters)"
        
        return None
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        import re
        # Remove or replace dangerous characters
        filename = re.sub(r'[^\w\s-.]', '', filename)
        filename = re.sub(r'[-\s]+', '-', filename)
        return filename.strip('-')


# Global error handler instance
error_handler = ErrorHandler()
validation_utils = ValidationUtils()
