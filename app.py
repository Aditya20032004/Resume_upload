"""
Day 14: Refactored AI Voice Agent Application
Clean, maintainable Flask application with proper structure
"""

import os
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
from pydantic import ValidationError

# Import our refactored modules
from config import config, logger
from models import (
    TTSRequest, TTSResponse, LLMRequest, VoiceQueryRequest, VoiceQueryResponse,
    HealthCheckResponse, ErrorType, MessageRole
)
from services import stt_service, llm_service, tts_service
from utils import chat_manager, error_handler, validation_utils


class VoiceAgentApp:
    """Main Voice Agent Application Class"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self._configure_app()
        self._register_routes()
        logger.info("Voice Agent Application initialized")
    
    def _configure_app(self):
        """Configure Flask application"""
        # File upload settings
        self.app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
        self.app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
        
        # Ensure uploads directory exists
        os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
        
        # Add CORS and security headers
        @self.app.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            response.headers.add('Permissions-Policy', 'microphone=(self), camera=(self)')
            return response
    
    def _register_routes(self):
        """Register all application routes"""
        
        @self.app.route('/')
        def index():
            """Serve the main application page"""
            return render_template('index.html')
        
        @self.app.route('/api/health')
        def health_check():
            """Health check endpoint with service status"""
            try:
                missing_keys = config.get_missing_keys()
                services_status = {
                    'stt': stt_service.is_available(),
                    'llm': llm_service.is_available(),
                    'tts': tts_service.is_available()
                }
                
                response = HealthCheckResponse(
                    status="healthy" if len(missing_keys) == 0 else "degraded",
                    services=services_status
                )
                
                return jsonify(response.model_dump())
                
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return jsonify({
                    "status": "unhealthy",
                    "error": str(e)
                }), 500
        
        @self.app.route('/api/tts', methods=['POST'])
        def text_to_speech():
            """Text-to-Speech endpoint"""
            try:
                # Validate request data
                data = request.get_json()
                if not data:
                    return jsonify(error_handler.create_error_response(
                        "Missing request body",
                        ErrorType.INPUT_ERROR
                    ).model_dump()), 400
                
                # Parse and validate request
                tts_request = TTSRequest(**data)
                
                # Process TTS request
                response = tts_service.synthesize_speech(tts_request)
                
                return jsonify(response.model_dump()), 200 if response.success else 500
                
            except ValidationError as e:
                logger.warning(f"TTS validation error: {e}")
                return jsonify(error_handler.create_error_response(
                    f"Invalid request data: {str(e)}",
                    ErrorType.INPUT_ERROR
                ).model_dump()), 400
            except Exception as e:
                logger.error(f"TTS endpoint error: {e}")
                return jsonify(error_handler.create_error_response(
                    "TTS processing failed",
                    ErrorType.GENERAL_ERROR
                ).model_dump()), 500
        
        @self.app.route('/api/transcribe', methods=['POST'])
        def transcribe_audio():
            """Audio transcription endpoint"""
            try:
                # Validate audio file
                if 'audio' not in request.files:
                    return jsonify(error_handler.create_error_response(
                        "No audio file provided",
                        ErrorType.INPUT_ERROR
                    ).model_dump()), 400
                
                audio_file = request.files['audio']
                validation_error = validation_utils.validate_audio_file(audio_file)
                if validation_error:
                    return jsonify(error_handler.create_error_response(
                        validation_error,
                        ErrorType.INPUT_ERROR
                    ).model_dump()), 400
                
                # Process transcription
                response = stt_service.transcribe_audio(audio_file)
                
                return jsonify(response.model_dump()), 200 if response.success else 500
                
            except Exception as e:
                logger.error(f"Transcription endpoint error: {e}")
                return jsonify(error_handler.create_error_response(
                    "Transcription processing failed",
                    ErrorType.GENERAL_ERROR
                ).model_dump()), 500
        
        @self.app.route('/llm/query', methods=['POST'])
        def llm_query():
            """LLM query endpoint - handles both text and voice requests"""
            try:
                # Check if this is a voice request (has audio file)
                if 'audio' in request.files:
                    return self._handle_voice_query()
                
                # Handle text query
                return self._handle_text_query()
                
            except Exception as e:
                logger.error(f"LLM endpoint error: {e}")
                return jsonify(error_handler.create_error_response(
                    "LLM processing failed",
                    ErrorType.GENERAL_ERROR
                ).model_dump()), 500
        
        def _handle_text_query(self):
            """Handle text-based LLM queries"""
            # Get text from request (support both JSON and form data)
            if request.is_json:
                data = request.get_json()
                text = data.get('text') if data else None
            else:
                text = request.form.get('text')
            
            if not text:
                return jsonify(error_handler.create_error_response(
                    "Missing 'text' field in request",
                    ErrorType.INPUT_ERROR
                ).model_dump()), 400
            
            # Validate text input
            validation_error = validation_utils.validate_text_input(text)
            if validation_error:
                return jsonify(error_handler.create_error_response(
                    validation_error,
                    ErrorType.INPUT_ERROR
                ).model_dump()), 400
            
            # Create LLM request
            llm_request = LLMRequest(text=text)
            
            # Process LLM query
            response = llm_service.generate_response(llm_request)
            
            return jsonify(response.model_dump())
        
        def _handle_voice_query(self):
            """Handle voice-based LLM queries (complete pipeline)"""
            # Validate audio file
            if 'audio' not in request.files:
                return jsonify(error_handler.create_error_response(
                    "No audio file provided",
                    ErrorType.INPUT_ERROR
                ).model_dump()), 400
            
            audio_file = request.files['audio']
            validation_error = validation_utils.validate_audio_file(audio_file)
            if validation_error:
                return jsonify(error_handler.create_error_response(
                    validation_error,
                    ErrorType.INPUT_ERROR
                ).model_dump()), 400
            
            # Get optional parameters
            session_id = request.form.get('session_id') or str(uuid.uuid4())
            
            # Process voice query pipeline
            response = self._process_voice_pipeline(audio_file, session_id)
            
            return jsonify(response.model_dump())
        
        @self.app.route('/api/chat/history/<session_id>')
        def get_chat_history(session_id):
            """Get chat history for a session"""
            try:
                history = chat_manager.get_chat_history(session_id)
                return jsonify({
                    "success": True,
                    "session_id": session_id,
                    "history": [msg.model_dump() for msg in history],
                    "message_count": len(history)
                })
            except Exception as e:
                logger.error(f"Chat history error: {e}")
                return jsonify(error_handler.create_error_response(
                    "Failed to retrieve chat history",
                    ErrorType.GENERAL_ERROR
                ).model_dump()), 500
        
        @self.app.route('/uploads/<filename>')
        def uploaded_file(filename):
            """Serve uploaded files"""
            return send_from_directory(config.UPLOAD_FOLDER, filename)
    
    def _handle_text_query(self):
        """Handle text-based LLM queries"""
        # Get text from request (support both JSON and form data)
        if request.is_json:
            data = request.get_json()
            text = data.get('text') if data else None
        else:
            text = request.form.get('text')
        
        if not text:
            return jsonify(error_handler.create_error_response(
                "Missing 'text' field in request",
                ErrorType.INPUT_ERROR
            ).model_dump()), 400
        
        # Validate text input
        validation_error = validation_utils.validate_text_input(text)
        if validation_error:
            return jsonify(error_handler.create_error_response(
                validation_error,
                ErrorType.INPUT_ERROR
            ).model_dump()), 400
        
        # Create LLM request
        llm_request = LLMRequest(text=text)
        
        # Process LLM query
        response = llm_service.generate_response(llm_request)
        
        return jsonify(response.model_dump())
    
    def _handle_voice_query(self):
        """Handle voice-based LLM queries (complete pipeline)"""
        # Validate audio file
        if 'audio' not in request.files:
            return jsonify(error_handler.create_error_response(
                "No audio file provided",
                ErrorType.INPUT_ERROR
            ).model_dump()), 400
        
        audio_file = request.files['audio']
        validation_error = validation_utils.validate_audio_file(audio_file)
        if validation_error:
            return jsonify(error_handler.create_error_response(
                validation_error,
                ErrorType.INPUT_ERROR
            ).model_dump()), 400
        
        # Get optional parameters
        session_id = request.form.get('session_id') or str(uuid.uuid4())
        
        # Process voice query pipeline
        response = self._process_voice_pipeline(audio_file, session_id)
        
        return jsonify(response.model_dump())
    
    def _process_voice_pipeline(self, audio_file, session_id: str) -> VoiceQueryResponse:
        """Process complete voice pipeline: STT -> LLM -> TTS"""
        try:
            # Step 1: Speech-to-Text
            logger.info("Processing voice pipeline - Step 1: STT")
            stt_response = stt_service.transcribe_audio(audio_file)
            
            if not stt_response.success:
                return VoiceQueryResponse(
                    success=False,
                    error=stt_response.error,
                    error_type=stt_response.error_type,
                    session_id=session_id
                )
            
            transcription = stt_response.transcription
            logger.info(f"Transcription: {transcription}")
            
            # Step 2: Add user message to chat history
            chat_manager.add_user_message(session_id, transcription)
            
            # Step 3: LLM Processing
            logger.info("Processing voice pipeline - Step 3: LLM")
            chat_history = chat_manager.get_recent_messages(session_id, 10)
            llm_request = LLMRequest(text=transcription, session_id=session_id)
            llm_response = llm_service.generate_response(llm_request, chat_history)
            
            if not llm_response.success:
                # Use fallback response
                response_text = llm_response.fallback_response or "I'm having trouble processing your request."
            else:
                response_text = llm_response.response
            
            # Step 4: Add assistant message to chat history
            chat_manager.add_assistant_message(session_id, response_text)
            
            # Step 5: Text-to-Speech
            logger.info("Processing voice pipeline - Step 5: TTS")
            tts_request = TTSRequest(text=response_text)
            tts_response = tts_service.synthesize_speech(tts_request)
            
            # Step 6: Prepare final response
            updated_history = chat_manager.get_chat_history(session_id)
            
            return VoiceQueryResponse(
                success=True,
                transcription=transcription,
                llm_response=response_text,
                audio_url=tts_response.audio_url if tts_response.success else None,
                confidence=stt_response.confidence,
                chat_history=updated_history,
                session_id=session_id,
                message_count=len(updated_history),
                fallback_used=not llm_response.success or not tts_response.success
            )
            
        except Exception as e:
            logger.error(f"Voice pipeline error: {e}")
            return VoiceQueryResponse(
                success=False,
                error=f"Voice processing failed: {str(e)}",
                error_type=ErrorType.GENERAL_ERROR,
                session_id=session_id
            )
    
    def run(self):
        """Run the Flask application"""
        logger.info("🌐 Starting AgentsAI Voice Agent server...")
        logger.info(f"🚀 Server will be available at: http://{config.HOST}:{config.PORT}")
        logger.info("🎙️ For microphone access:")
        logger.info(f"   1. Try http://{config.HOST}:{config.PORT} first")
        logger.info("   2. If microphone fails, try Chrome with --allow-running-insecure-content flag")
        logger.info("   3. Or use Firefox which is more permissive for localhost")
        
        # Check configuration
        missing_keys = config.get_missing_keys()
        if missing_keys:
            logger.warning(f"⚠️  Missing API keys: {', '.join(missing_keys)}")
            logger.warning("⚠️  Some features may not work properly")
        else:
            logger.info("✅ All API keys configured")
        
        self.app.run(
            debug=config.DEBUG,
            host=config.HOST,
            port=config.PORT
        )


# Create application instance
app_instance = VoiceAgentApp()

# Export Flask app for WSGI servers
app = app_instance.app


if __name__ == '__main__':
    app_instance.run()
