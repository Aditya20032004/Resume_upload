// Day 11: Enhanced Error Handling for Client-Side
// Error handling utilities and fallback mechanisms

// Global error handling variables
let speechSynthesis = null;
let fallbackErrorCount = 0;
const MAX_FALLBACK_ATTEMPTS = 3;

// Initialize speech synthesis for fallback TTS
function initializeFallbackTTS() {
    if ('speechSynthesis' in window) {
        speechSynthesis = window.speechSynthesis;
        console.log('Browser speech synthesis initialized for fallback');
        return true;
    } else {
        console.warn('Speech synthesis not supported in this browser');
        return false;
    }
}

// Fallback TTS using browser's built-in speech synthesis
function speakTextFallback(text, options = {}) {
    return new Promise((resolve, reject) => {
        if (!speechSynthesis) {
            if (!initializeFallbackTTS()) {
                reject(new Error('Speech synthesis not available'));
                return;
            }
        }

        // Cancel any ongoing speech
        speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        
        // Set voice properties
        utterance.rate = options.rate || 1.0;
        utterance.pitch = options.pitch || 1.0;
        utterance.volume = options.volume || 1.0;
        
        // Try to use a specific voice
        const voices = speechSynthesis.getVoices();
        const preferredVoice = voices.find(voice => 
            voice.lang.startsWith('en') && voice.name.includes('Google')
        ) || voices.find(voice => voice.lang.startsWith('en')) || voices[0];
        
        if (preferredVoice) {
            utterance.voice = preferredVoice;
        }

        utterance.onend = () => {
            console.log('Fallback TTS completed');
            resolve();
        };

        utterance.onerror = (event) => {
            console.error('Fallback TTS error:', event.error);
            reject(new Error(`Speech synthesis failed: ${event.error}`));
        };

        speechSynthesis.speak(utterance);
    });
}

// Enhanced error display with fallback audio
function showErrorWithFallback(message, fallbackAudio = null, canRetry = true) {
    console.error('Error occurred:', message);
    
    // Display visual error
    const errorContainer = document.getElementById('errorContainer') || createErrorContainer();
    
    const timestamp = new Date().toLocaleTimeString();
    const errorId = Date.now();
    
    const errorHtml = `
        <div class="error-item" id="error-${errorId}">
            <div class="error-header">
                <span class="error-icon">⚠️</span>
                <span class="error-title">Connection Issue</span>
                <span class="error-time">${timestamp}</span>
                <button class="error-close" onclick="closeError(${errorId})">×</button>
            </div>
            <div class="error-message">${message}</div>
            <div class="error-actions">
                ${canRetry ? '<button class="retry-btn" onclick="retryLastAction()">🔄 Retry</button>' : ''}
                <button class="fallback-audio-btn" onclick="playErrorFallback(\`${message}\`)">🔊 Listen</button>
            </div>
        </div>
    `;
    
    errorContainer.insertAdjacentHTML('afterbegin', errorHtml);
    errorContainer.style.display = 'block';
    
    // Auto-remove after 10 seconds
    setTimeout(() => closeError(errorId), 10000);
    
    // Try to play fallback audio
    if (fallbackAudio) {
        playFallbackAudio(fallbackAudio);
    } else {
        // Use browser TTS as last resort
        setTimeout(() => {
            speakTextFallback(message).catch(console.error);
        }, 500);
    }
}

// Play fallback audio from base64 data or use browser TTS
function playFallbackAudio(audioData) {
    try {
        if (audioData && audioData.startsWith('data:text/plain;base64,')) {
            // Decode base64 text and use browser TTS
            const base64Text = audioData.split(',')[1];
            const decodedText = atob(base64Text);
            speakTextFallback(decodedText).catch(console.error);
        } else if (audioData && audioData.startsWith('http')) {
            // Try to play audio URL
            const audio = new Audio(audioData);
            audio.play().catch(error => {
                console.warn('Fallback audio playback failed, using TTS:', error);
                speakTextFallback("I'm having trouble playing audio right now").catch(console.error);
            });
        } else {
            console.warn('Invalid fallback audio data');
        }
    } catch (error) {
        console.error('Fallback audio processing failed:', error);
        speakTextFallback("I'm experiencing technical difficulties").catch(console.error);
    }
}

// Create error container if it doesn't exist
function createErrorContainer() {
    const container = document.createElement('div');
    container.id = 'errorContainer';
    container.className = 'error-container';
    container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        max-width: 400px;
        z-index: 10000;
        display: none;
    `;
    document.body.appendChild(container);
    return container;
}

// Enhanced chat processing with comprehensive error handling
async function processLLMRecordingWithErrorHandling(audioBlob) {
    const maxRetries = 2;
    let lastError = null;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            console.log(`Processing attempt ${attempt}/${maxRetries}`);
            
            // Show processing indicator
            if (llmResult) {
                llmResult.innerHTML = `
                    <div class="processing-indicator">
                        <div class="spinner"></div>
                        <p>Processing your message... (Attempt ${attempt})</p>
                        <small>STT → LLM → TTS Pipeline</small>
                    </div>
                `;
                llmResult.classList.add('show');
            }
            
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');
            
            // Get or generate session ID
            let sessionId = localStorage.getItem('chat_session_id');
            if (!sessionId) {
                sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                localStorage.setItem('chat_session_id', sessionId);
            }
            
            const response = await fetch(`/agent/chat/${sessionId}`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                displayLLMResultWithFallbacks(result);
                
                // Display chat history
                if (result.chat_history) {
                    displayChatHistory(result.chat_history);
                }
                
                return; // Success, exit retry loop
                
            } else {
                // Handle server-side errors with fallback
                const errorType = result.error_type || 'general_error';
                const fallbackMessage = result.fallback_message || result.error || 'Processing failed';
                const fallbackAudio = result.fallback_audio;
                
                if (errorType === 'stt_error') {
                    showErrorWithFallback(
                        "I couldn't understand your recording clearly. Please try speaking more clearly and closer to the microphone.",
                        fallbackAudio
                    );
                } else if (errorType === 'llm_error') {
                    showErrorWithFallback(
                        "I'm having trouble connecting to my AI brain. Let me try to help you anyway.",
                        fallbackAudio
                    );
                } else if (errorType === 'tts_error') {
                    showErrorWithFallback(
                        "I understood you, but I'm having trouble speaking right now. Check the text response below.",
                        fallbackAudio
                    );
                } else {
                    throw new Error(fallbackMessage);
                }
                
                // If we have a partial response (e.g., text but no audio), display it
                if (result.transcription || result.llm_response) {
                    displayPartialLLMResult(result);
                }
                
                return; // Don't retry for handled errors
            }
            
        } catch (error) {
            console.error(`Attempt ${attempt} failed:`, error);
            lastError = error;
            
            if (attempt < maxRetries) {
                // Wait before retry
                await new Promise(resolve => setTimeout(resolve, 2000));
                continue;
            }
        }
    }
    
    // All retries failed
    const errorMessage = lastError?.message || 'Network error after multiple attempts';
    showErrorWithFallback(
        `I'm having trouble connecting right now. Please check your internet connection and try again. (${errorMessage})`,
        null,
        true
    );
    
    // Show retry option
    if (llmResult) {
        llmResult.innerHTML = `
            <div class="error-message">
                <h3>❌ Connection Failed</h3>
                <p>I couldn't process your message after ${maxRetries} attempts.</p>
                <p class="error-details">${errorMessage}</p>
                <div class="error-actions">
                    <button onclick="retryLastAction()" class="retry-btn">🔄 Try Again</button>
                    <button onclick="clearErrorState()" class="clear-btn">✖️ Clear</button>
                </div>
                <div class="offline-help">
                    <h4>Troubleshooting:</h4>
                    <ul>
                        <li>Check your internet connection</li>
                        <li>Try speaking more clearly</li>
                        <li>Ensure microphone permissions are granted</li>
                        <li>Refresh the page if problems persist</li>
                    </ul>
                </div>
            </div>
        `;
        llmResult.classList.add('show');
    }
}

// Display results with fallback handling
function displayLLMResultWithFallbacks(result) {
    console.log('LLM Result with fallbacks:', result);
    
    if (llmResult) {
        const hasAudio = result.audio_url && !result.tts_failed;
        const isUsingFallback = result.tts_fallback || result.tts_failed;
        
        llmResult.innerHTML = `
            <div class="llm-success">
                <h3>🧠 AI Assistant Response</h3>
                
                <div class="transcription-section">
                    <h4>🎙️ Your Question:</h4>
                    <p class="transcription-text">"${result.transcription}"</p>
                    ${result.confidence !== undefined ? `<small>Confidence: ${(result.confidence * 100).toFixed(1)}%</small>` : ''}
                </div>
                
                <div class="llm-response-section">
                    <h4>🤖 AI Response:</h4>
                    <p class="llm-response-text">${result.llm_response}</p>
                </div>
                
                <div class="audio-response-section">
                    <h4>🔊 Listen to Response:</h4>
                    ${hasAudio ? 
                        `<audio controls class="response-audio">
                            <source src="${result.audio_url}" type="audio/mpeg">
                            Your browser does not support audio playback.
                        </audio>
                        ${isUsingFallback ? '<p class="fallback-notice">⚠️ Using backup audio system</p>' : ''}
                        <div class="audio-controls">
                            <button onclick="playResponseWithFallback('${result.llm_response}')" class="fallback-tts-btn">
                                🔊 Use Browser Voice
                            </button>
                        </div>` 
                        : `<div class="audio-fallback">
                            <p class="audio-error">🚫 Audio generation failed</p>
                            <button onclick="playResponseWithFallback('${result.llm_response}')" class="fallback-tts-btn">
                                🔊 Listen with Browser Voice
                            </button>
                           </div>`
                    }
                    <p class="audio-info">Session: ${result.session_id}</p>
                </div>
                
                <div class="pipeline-info">
                    <small>🔄 Pipeline: Audio → STT → LLM → TTS → Response</small>
                    ${result.message_count ? `<br><small>💬 Messages: ${result.message_count}</small>` : ''}
                    ${result.warning ? `<br><small class="warning">⚠️ ${result.warning}</small>` : ''}
                </div>
            </div>
        `;
        
        llmResult.classList.add('show');
        
        // Handle audio playback with fallbacks
        if (hasAudio) {
            const audio = llmResult.querySelector('.response-audio');
            if (audio) {
                audio.onended = () => {
                    setTimeout(() => startLLMRecording(), 1000);
                };
                
                audio.onerror = () => {
                    console.warn('Audio playback failed, using browser TTS');
                    playResponseWithFallback(result.llm_response);
                };
                
                setTimeout(() => {
                    audio.play().catch(e => {
                        console.log('Auto-play prevented, showing manual play option');
                    });
                }, 500);
            }
        } else {
            // No audio available, auto-play with browser TTS
            setTimeout(() => {
                playResponseWithFallback(result.llm_response);
            }, 1000);
        }
    }
}

// Play response using browser TTS fallback
function playResponseWithFallback(text) {
    speakTextFallback(text, { rate: 1.1, pitch: 1.0 })
        .then(() => {
            setTimeout(() => startLLMRecording(), 1000);
        })
        .catch(error => {
            console.error('Fallback TTS failed:', error);
            showErrorWithFallback("I can't speak right now, but you can read my response above.");
        });
}

// Display partial results when some components fail
function displayPartialLLMResult(result) {
    if (llmResult) {
        llmResult.innerHTML = `
            <div class="llm-partial">
                <h3>⚠️ Partial Response</h3>
                
                ${result.transcription ? `
                    <div class="transcription-section">
                        <h4>🎙️ What I heard:</h4>
                        <p class="transcription-text">"${result.transcription}"</p>
                    </div>
                ` : ''}
                
                ${result.llm_response ? `
                    <div class="llm-response-section">
                        <h4>🤖 My response:</h4>
                        <p class="llm-response-text">${result.llm_response}</p>
                        <button onclick="playResponseWithFallback('${result.llm_response}')" class="fallback-tts-btn">
                            🔊 Listen with Browser Voice
                        </button>
                    </div>
                ` : ''}
                
                <div class="partial-notice">
                    <p>Some features are temporarily unavailable, but I'm still here to help!</p>
                </div>
            </div>
        `;
        llmResult.classList.add('show');
    }
}

// Utility functions for error handling
function closeError(errorId) {
    const errorElement = document.getElementById(`error-${errorId}`);
    if (errorElement) {
        errorElement.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => errorElement.remove(), 300);
    }
}

function playErrorFallback(message) {
    speakTextFallback(message).catch(console.error);
}

function retryLastAction() {
    // This would be set by the last failed action
    if (window.lastFailedAction) {
        window.lastFailedAction();
    } else {
        showErrorWithFallback("No action to retry. Please try your request again.", null, false);
    }
}

function clearErrorState() {
    if (llmResult) {
        llmResult.classList.remove('show');
        llmResult.innerHTML = '';
    }
    
    const errorContainer = document.getElementById('errorContainer');
    if (errorContainer) {
        errorContainer.style.display = 'none';
        errorContainer.innerHTML = '';
    }
}

// Initialize error handling when DOM loads
document.addEventListener('DOMContentLoaded', function() {
    initializeFallbackTTS();
    
    // Override the original processLLMRecording function
    if (typeof processLLMRecording !== 'undefined') {
        const originalProcessLLMRecording = processLLMRecording;
        window.processLLMRecording = function(audioBlob) {
            window.lastFailedAction = () => originalProcessLLMRecording(audioBlob);
            return processLLMRecordingWithErrorHandling(audioBlob);
        };
    }
    
    console.log('Day 11: Error handling and fallback systems initialized');
});

// Add CSS for error handling (if not already present)
if (!document.getElementById('error-handling-css')) {
    const css = document.createElement('style');
    css.id = 'error-handling-css';
    css.textContent = `
        .error-container {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .error-item {
            background: #fee;
            border: 1px solid #fcc;
            border-radius: 8px;
            margin-bottom: 10px;
            padding: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            animation: slideIn 0.3s ease-out;
        }
        
        .error-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }
        
        .error-icon {
            font-size: 16px;
            margin-right: 8px;
        }
        
        .error-title {
            font-weight: 600;
            color: #c53030;
            flex: 1;
        }
        
        .error-time {
            font-size: 12px;
            color: #666;
            margin-right: 8px;
        }
        
        .error-close {
            background: none;
            border: none;
            font-size: 18px;
            cursor: pointer;
            color: #999;
            padding: 0;
            width: 20px;
            height: 20px;
        }
        
        .error-message {
            color: #742a2a;
            margin-bottom: 8px;
            line-height: 1.4;
        }
        
        .error-actions {
            display: flex;
            gap: 8px;
        }
        
        .retry-btn, .fallback-audio-btn, .fallback-tts-btn, .clear-btn {
            background: #e53e3e;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            transition: background-color 0.2s;
        }
        
        .retry-btn:hover, .fallback-audio-btn:hover, .fallback-tts-btn:hover {
            background: #c53030;
        }
        
        .clear-btn {
            background: #718096;
        }
        
        .clear-btn:hover {
            background: #4a5568;
        }
        
        .fallback-notice {
            color: #d69e2e;
            font-style: italic;
            font-size: 12px;
            margin-top: 4px;
        }
        
        .audio-fallback {
            background: #fffbeb;
            border: 1px solid #f6e05e;
            border-radius: 4px;
            padding: 12px;
            margin: 8px 0;
        }
        
        .audio-error {
            color: #c53030;
            margin: 0 0 8px 0;
        }
        
        .warning {
            color: #d69e2e;
        }
        
        .processing-indicator {
            text-align: center;
            padding: 20px;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #3498db;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px auto;
        }
        
        .offline-help {
            background: #f7fafc;
            border-radius: 4px;
            padding: 12px;
            margin-top: 12px;
        }
        
        .offline-help h4 {
            margin: 0 0 8px 0;
            color: #2d3748;
        }
        
        .offline-help ul {
            margin: 0;
            padding-left: 20px;
        }
        
        .offline-help li {
            margin: 4px 0;
            color: #4a5568;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(100%);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes slideOut {
            from {
                opacity: 1;
                transform: translateX(0);
            }
            to {
                opacity: 0;
                transform: translateX(100%);
            }
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(css);
}
