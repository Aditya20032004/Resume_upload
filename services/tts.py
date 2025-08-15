"""
Day 14: Text-to-Speech Service
Handles speech synthesis using Murf API
"""

import requests
import base64
from typing import Optional

from config import config, logger
from models import TTSRequest, TTSResponse, ErrorType


class TTSService:
    """Text-to-Speech service using Murf API"""
    
    def __init__(self):
        self.api_key = config.MURF_API_KEY
        self.api_url = config.MURF_API_URL
        self.timeout = config.TTS_TIMEOUT
        self.default_voice = config.DEFAULT_VOICE_ID
        self.default_speed = config.DEFAULT_SPEECH_SPEED
        self.default_pitch = config.DEFAULT_SPEECH_PITCH
    
    def is_available(self) -> bool:
        """Check if TTS service is available"""
        return (self.api_key is not None and 
                self.api_key != 'your_murf_api_key_here' and
                self.api_url is not None and
                self.api_url != 'your_murf_api_url_here')
    
    def synthesize_speech(self, request: TTSRequest) -> TTSResponse:
        """
        Convert text to speech using Murf API
        
        Args:
            request: TTS request with text and voice parameters
            
        Returns:
            TTSResponse with audio URL or error
        """
        if not self.is_available():
            emergency_fallback = self._generate_emergency_fallback(request.text)
            return TTSResponse(
                success=False,
                error="TTS service not available - API keys not configured",
                error_type=ErrorType.CONFIG_ERROR,
                emergency_fallback=emergency_fallback
            )
        
        try:
            # Prepare Murf API request
            payload = self._prepare_murf_payload(request)
            headers = self._prepare_murf_headers()
            
            # Make API call to Murf
            logger.info(f"Calling Murf API for TTS: {request.text[:50]}...")
            response = requests.post(
                self.api_url, 
                json=payload, 
                headers=headers, 
                timeout=self.timeout
            )
            
            # Process response
            return self._process_murf_response(response, request.text)
            
        except requests.exceptions.Timeout:
            logger.error("Murf API timeout")
            emergency_fallback = self._generate_emergency_fallback(request.text)
            return TTSResponse(
                success=False,
                error="TTS request timed out",
                error_type=ErrorType.TIMEOUT_ERROR,
                emergency_fallback=emergency_fallback
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Murf API request failed: {e}")
            emergency_fallback = self._generate_emergency_fallback(request.text)
            return TTSResponse(
                success=False,
                error=f"TTS API request failed: {str(e)}",
                error_type=ErrorType.NETWORK_ERROR,
                emergency_fallback=emergency_fallback
            )
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            emergency_fallback = self._generate_emergency_fallback(request.text)
            return TTSResponse(
                success=False,
                error=f"TTS synthesis failed: {str(e)}",
                error_type=ErrorType.TTS_ERROR,
                emergency_fallback=emergency_fallback
            )
    
    def _prepare_murf_payload(self, request: TTSRequest) -> dict:
        """Prepare payload for Murf API"""
        return {
            "voiceId": request.voice_id or self.default_voice,
            "style": "Conversational",
            "text": request.text,
            "rate": request.speed or self.default_speed,
            "pitch": request.pitch or self.default_pitch,
            "sampleRate": 24000,
            "format": "MP3",
            "channelType": "MONO",
            "pronunciationDictionary": {},
            "encodeAsBase64": False,
            "variation": 1,
            "audioDuration": 0,
            "modelVersion": "GEN2"
        }
    
    def _prepare_murf_headers(self) -> dict:
        """Prepare headers for Murf API"""
        return {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def _process_murf_response(self, response: requests.Response, original_text: str) -> TTSResponse:
        """Process Murf API response"""
        if response.status_code != 200:
            logger.error(f"Murf API error: {response.status_code} - {response.text}")
            emergency_fallback = self._generate_emergency_fallback(original_text)
            return TTSResponse(
                success=False,
                error=f"TTS API returned status {response.status_code}",
                error_type=ErrorType.API_ERROR,
                emergency_fallback=emergency_fallback
            )
        
        try:
            data = response.json()
            audio_url = data.get("audioFile")
            
            if not audio_url:
                logger.error("No audio URL in Murf response")
                emergency_fallback = self._generate_emergency_fallback(original_text)
                return TTSResponse(
                    success=False,
                    error="No audio URL returned from TTS service",
                    error_type=ErrorType.TTS_ERROR,
                    emergency_fallback=emergency_fallback
                )
            
            logger.info("TTS synthesis successful")
            return TTSResponse(
                success=True,
                audio_url=audio_url
            )
            
        except ValueError as e:
            logger.error(f"Failed to parse Murf response: {e}")
            emergency_fallback = self._generate_emergency_fallback(original_text)
            return TTSResponse(
                success=False,
                error="Invalid response format from TTS service",
                error_type=ErrorType.API_ERROR,
                emergency_fallback=emergency_fallback
            )
    
    def _generate_emergency_fallback(self, text: str) -> Optional[str]:
        """Generate emergency TTS fallback using base64 encoding for client-side synthesis"""
        try:
            # Create a data URL that the frontend can use with Web Speech API
            text_bytes = text.encode('utf-8')
            base64_text = base64.b64encode(text_bytes).decode('utf-8')
            return f"data:text/plain;base64,{base64_text}"
        except Exception as e:
            logger.error(f"Emergency TTS fallback failed: {e}")
            return None
    
    def health_check(self) -> dict:
        """Check TTS service health"""
        return {
            "service": "Murf API",
            "available": self.is_available(),
            "api_key_configured": bool(self.api_key and self.api_key != 'your_murf_api_key_here'),
            "api_url_configured": bool(self.api_url and self.api_url != 'your_murf_api_url_here'),
            "timeout": self.timeout,
            "default_voice": self.default_voice
        }


# Global TTS service instance
tts_service = TTSService()
