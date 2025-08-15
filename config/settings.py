"""
Day 14: Configuration Management
Centralized configuration with environment variable validation
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration class"""
    
    # Flask Configuration
    DEBUG: bool = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST: str = os.getenv('HOST', 'localhost')
    PORT: int = int(os.getenv('PORT', '5000'))
    
    # File Upload Configuration
    UPLOAD_FOLDER: str = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH: int = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB
    
    # API Keys
    ASSEMBLYAI_API_KEY: Optional[str] = os.getenv('ASSEMBLYAI_API_KEY', '').strip("'\"")
    GEMINI_API_KEY: Optional[str] = os.getenv('GEMINI_API_KEY', '').strip("'\"")
    MURF_API_KEY: Optional[str] = os.getenv('MURF_API_KEY', '').strip("'\"")
    MURF_API_URL: Optional[str] = os.getenv('MURF_API_URL', '').strip("'\"")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO').upper()
    LOG_FORMAT: str = os.getenv('LOG_FORMAT', 
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Service Configuration
    STT_SERVICE: str = os.getenv('STT_SERVICE', 'assemblyai')
    LLM_SERVICE: str = os.getenv('LLM_SERVICE', 'gemini')
    TTS_SERVICE: str = os.getenv('TTS_SERVICE', 'murf')
    
    # Default Voice Configuration
    DEFAULT_VOICE_ID: str = os.getenv('DEFAULT_VOICE_ID', 'en-US-AriaNeural')
    DEFAULT_SPEECH_SPEED: int = int(os.getenv('DEFAULT_SPEECH_SPEED', '95'))
    DEFAULT_SPEECH_PITCH: int = int(os.getenv('DEFAULT_SPEECH_PITCH', '45'))
    
    # Timeout Configuration
    STT_TIMEOUT: int = int(os.getenv('STT_TIMEOUT', '30'))
    LLM_TIMEOUT: int = int(os.getenv('LLM_TIMEOUT', '30'))
    TTS_TIMEOUT: int = int(os.getenv('TTS_TIMEOUT', '60'))
    
    @classmethod
    def validate_api_keys(cls) -> dict:
        """Validate that required API keys are present"""
        validation_results = {
            'assemblyai': bool(cls.ASSEMBLYAI_API_KEY and 
                             cls.ASSEMBLYAI_API_KEY != 'your_assemblyai_api_key_here'),
            'gemini': bool(cls.GEMINI_API_KEY and 
                          cls.GEMINI_API_KEY != 'your_gemini_api_key_here'),
            'murf': bool(cls.MURF_API_KEY and 
                        cls.MURF_API_KEY != 'your_murf_api_key_here'),
            'murf_url': bool(cls.MURF_API_URL and 
                           cls.MURF_API_URL != 'your_murf_api_url_here')
        }
        return validation_results
    
    @classmethod
    def get_missing_keys(cls) -> list:
        """Get list of missing API keys"""
        validation = cls.validate_api_keys()
        return [key for key, valid in validation.items() if not valid]
    
    @classmethod
    def is_production_ready(cls) -> bool:
        """Check if all required configuration is present for production"""
        missing_keys = cls.get_missing_keys()
        return len(missing_keys) == 0


def setup_logging(config: Config = None) -> logging.Logger:
    """Setup logging configuration"""
    if config is None:
        config = Config()
    
    # Set logging level
    log_level = getattr(logging, config.LOG_LEVEL, logging.INFO)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format=config.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log', mode='a')
        ]
    )
    
    # Create logger
    logger = logging.getLogger('agentsai')
    logger.setLevel(log_level)
    
    return logger


# Global configuration instance
config = Config()

# Setup logger
logger = setup_logging(config)
