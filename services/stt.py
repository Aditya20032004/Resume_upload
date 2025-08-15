"""
Day 14: Speech-to-Text Service
Handles audio transcription using AssemblyAI
"""

import os
import tempfile
import requests
import assemblyai as aai
from typing import Tuple, Optional
from werkzeug.datastructures import FileStorage

from config import config, logger
from models import TranscriptionResponse, ErrorType


class STTService:
    """Speech-to-Text service using AssemblyAI"""
    
    def __init__(self):
        self.api_key = config.ASSEMBLYAI_API_KEY
        self.timeout = config.STT_TIMEOUT
        self._setup_client()
    
    def _setup_client(self) -> None:
        """Setup AssemblyAI client"""
        if not self.api_key or self.api_key == 'your_assemblyai_api_key_here':
            logger.warning("AssemblyAI API key not configured")
            self.client = None
            return
        
        try:
            aai.settings.api_key = self.api_key
            self.client = aai
            logger.info("AssemblyAI client configured successfully")
        except Exception as e:
            logger.error(f"Failed to setup AssemblyAI client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if STT service is available"""
        return self.client is not None and self.api_key is not None
    
    def transcribe_audio(self, audio_file: FileStorage) -> TranscriptionResponse:
        """
        Transcribe audio file to text
        
        Args:
            audio_file: Uploaded audio file
            
        Returns:
            TranscriptionResponse with transcription result
        """
        if not self.is_available():
            return TranscriptionResponse(
                success=False,
                error="STT service not available - API key not configured",
                error_type=ErrorType.CONFIG_ERROR
            )
        
        temp_file_path = None
        try:
            # Save uploaded file to temporary location
            temp_file_path = self._save_temp_file(audio_file)
            
            # Perform transcription
            transcription_result = self._perform_transcription(temp_file_path)
            
            return transcription_result
            
        except Exception as e:
            logger.error(f"STT transcription failed: {e}")
            return TranscriptionResponse(
                success=False,
                error=f"Transcription failed: {str(e)}",
                error_type=ErrorType.STT_ERROR
            )
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp file: {e}")
    
    def _save_temp_file(self, audio_file: FileStorage) -> str:
        """Save uploaded file to temporary location"""
        # Create temporary file
        temp_fd, temp_file_path = tempfile.mkstemp(suffix='.webm')
        
        try:
            # Save uploaded file
            with os.fdopen(temp_fd, 'wb') as temp_file:
                audio_file.save(temp_file)
            
            logger.info(f"Saved audio file to: {temp_file_path}")
            return temp_file_path
            
        except Exception as e:
            # Clean up file descriptor if saving failed
            try:
                os.close(temp_fd)
                os.unlink(temp_file_path)
            except:
                pass
            raise e
    
    def _perform_transcription(self, audio_file_path: str) -> TranscriptionResponse:
        """Perform the actual transcription using AssemblyAI"""
        try:
            # Create transcriber
            transcriber = self.client.Transcriber()
            
            # Perform transcription
            logger.info("Starting AssemblyAI transcription...")
            transcript = transcriber.transcribe(audio_file_path)
            
            # Check transcription status
            if transcript.status == self.client.TranscriptStatus.error:
                logger.error(f"AssemblyAI transcription error: {transcript.error}")
                return TranscriptionResponse(
                    success=False,
                    error=f"Transcription service error: {transcript.error}",
                    error_type=ErrorType.STT_ERROR
                )
            
            # Extract transcription text
            transcription_text = transcript.text
            confidence = transcript.confidence if hasattr(transcript, 'confidence') else None
            
            if not transcription_text or transcription_text.strip() == "":
                logger.warning("Empty transcription received")
                return TranscriptionResponse(
                    success=False,
                    error="No speech detected in audio",
                    error_type=ErrorType.STT_ERROR
                )
            
            logger.info(f"Transcription successful: {transcription_text[:100]}...")
            return TranscriptionResponse(
                success=True,
                transcription=transcription_text.strip(),
                confidence=confidence,
                language="en"
            )
            
        except Exception as e:
            logger.error(f"AssemblyAI transcription failed: {e}")
            return TranscriptionResponse(
                success=False,
                error=f"Transcription processing failed: {str(e)}",
                error_type=ErrorType.STT_ERROR
            )
    
    def health_check(self) -> dict:
        """Check STT service health"""
        return {
            "service": "AssemblyAI",
            "available": self.is_available(),
            "api_key_configured": bool(self.api_key and self.api_key != 'your_assemblyai_api_key_here'),
            "timeout": self.timeout
        }


# Global STT service instance
stt_service = STTService()
