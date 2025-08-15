// Day 12: Modern Voice Button - Single Toggle Interface
// This replaces the old start/stop button system with a smart single button

class VoiceAssistant {
    constructor() {
        this.isRecording = false;
        this.isProcessing = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.recordingTimer = null;
        this.recordingStartTime = null;
        
        // DOM Elements
        this.voiceButton = document.getElementById('voiceButton');
        this.buttonText = this.voiceButton.querySelector('.button-text');
        this.recordingTimer = this.voiceButton.querySelector('.recording-timer');
        this.statusMessage = document.querySelector('.status-message');
        this.llmResult = document.getElementById('llmResult');
        this.chatHistory = document.getElementById('chat-history');
        
        // Initialize
        this.init();
    }
    
    init() {
        // Bind events
        this.voiceButton.addEventListener('click', () => this.handleVoiceButtonClick());
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && !e.target.matches('input, textarea')) {
                e.preventDefault();
                this.handleVoiceButtonClick();
            }
            if (e.code === 'Escape' && this.isRecording) {
                e.preventDefault();
                this.stopRecording();
            }
        });
        
        console.log('🎙️ Voice Assistant initialized - Day 12 Modern UI');
    }
    
    async handleVoiceButtonClick() {
        if (this.isProcessing) {
            console.log('🔄 Currently processing, please wait...');
            return;
        }
        
        if (!this.isRecording) {
            await this.startRecording();
        } else {
            await this.stopRecording();
        }
    }
    
    async startRecording() {
        try {
            console.log('🎙️ Starting recording...');
            
            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                } 
            });
            
            // Set up MediaRecorder
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = async () => {
                console.log('📀 Recording stopped, processing...');
                await this.processRecording();
            };
            
            // Start recording
            this.mediaRecorder.start();
            this.isRecording = true;
            this.recordingStartTime = Date.now();
            
            // Update UI
            this.updateButtonState('recording');
            this.updateStatus('🎙️ Recording... Tap again to stop');
            this.startTimer();
            
        } catch (error) {
            console.error('❌ Error starting recording:', error);
            this.updateStatus('❌ Microphone access denied. Please enable microphone permissions.');
            this.showError('Failed to access microphone. Please check your permissions.');
        }
    }
    
    async stopRecording() {
        if (!this.isRecording || !this.mediaRecorder) {
            return;
        }
        
        console.log('⏹️ Stopping recording...');
        
        // Stop the recording
        this.mediaRecorder.stop();
        this.isRecording = false;
        
        // Stop all tracks to release microphone
        this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        
        // Update UI
        this.updateButtonState('processing');
        this.updateStatus('🔄 Processing your voice...');
        this.stopTimer();
    }
    
    async processRecording() {
        this.isProcessing = true;
        
        try {
            // Create audio blob
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
            console.log(`📦 Audio blob created: ${audioBlob.size} bytes`);
            
            if (audioBlob.size < 1000) {
                throw new Error('Recording too short. Please speak for at least 1 second.');
            }
            
            // Create form data
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');
            
            // Get session ID
            const sessionId = document.getElementById('session-id').value.trim() || this.generateSessionId();
            formData.append('session_id', sessionId);
            
            // Update status
            this.updateStatus('🧠 AI is thinking...');
            
            // Send to server
            const response = await fetch('/llm/query', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Server error: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('✅ Server response:', result);
            
            // Display results
            this.displayResult(result);
            this.updateChatHistory(result);
            
            // Auto-play response if available
            if (result.audio_url) {
                this.playAudioResponse(result.audio_url);
            }
            
            this.updateStatus('✅ Response ready!');
            
        } catch (error) {
            console.error('❌ Processing error:', error);
            this.showError(error.message);
            this.updateStatus('❌ Processing failed');
        } finally {
            this.isProcessing = false;
            this.updateButtonState('idle');
        }
    }
    
    updateButtonState(state) {
        this.voiceButton.setAttribute('data-state', state);
        
        switch (state) {
            case 'idle':
                this.buttonText.textContent = 'Tap to Speak';
                break;
            case 'recording':
                this.buttonText.textContent = 'Recording...';
                break;
            case 'processing':
                this.buttonText.textContent = 'Processing...';
                break;
        }
    }
    
    updateStatus(message) {
        if (this.statusMessage) {
            this.statusMessage.textContent = message;
        }
    }
    
    startTimer() {
        this.stopTimer(); // Clear any existing timer
        
        const updateTimer = () => {
            if (!this.isRecording) return;
            
            const elapsed = Date.now() - this.recordingStartTime;
            const seconds = Math.floor(elapsed / 1000);
            const minutes = Math.floor(seconds / 60);
            const displaySeconds = seconds % 60;
            
            const timeString = `${minutes.toString().padStart(2, '0')}:${displaySeconds.toString().padStart(2, '0')}`;
            this.recordingTimer.textContent = timeString;
        };
        
        updateTimer(); // Initial update
        this.timerInterval = setInterval(updateTimer, 1000);
    }
    
    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        this.recordingTimer.textContent = '00:00';
    }
    
    displayResult(result) {
        if (!this.llmResult) return;
        
        const resultHTML = `
            <div class="response-container">
                <h4>💬 Conversation Result</h4>
                
                <div class="transcription">
                    <strong>🎤 You said:</strong><br>
                    "${result.transcription || 'No transcription available'}"
                </div>
                
                <div class="llm-response">
                    <strong>🤖 AI Response:</strong><br>
                    ${result.llm_response || 'No response generated'}
                </div>
                
                ${result.audio_url ? `
                    <div class="audio-response">
                        <strong>🔊 Voice Response:</strong><br>
                        <audio controls preload="metadata" style="width: 100%; margin-top: 10px;">
                            <source src="${result.audio_url}" type="audio/mpeg">
                            Your browser does not support the audio element.
                        </audio>
                    </div>
                ` : ''}
                
                <div class="metadata">
                    <small>
                        Session: ${result.session_id || 'N/A'} | 
                        Pipeline: Audio → Transcription → LLM → TTS → Response
                    </small>
                </div>
            </div>
        `;
        
        this.llmResult.innerHTML = resultHTML;
        
        // Smooth scroll to results
        this.llmResult.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    updateChatHistory(result) {
        if (!this.chatHistory) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const entry = document.createElement('div');
        entry.className = 'chat-entry';
        entry.innerHTML = `
            <div class="timestamp">🕐 ${timestamp}</div>
            <div class="user-question">
                <strong>You:</strong> ${result.transcription || 'No transcription'}
            </div>
            <div class="ai-response">
                <strong>AI:</strong> ${result.llm_response || 'No response'}
            </div>
        `;
        
        this.chatHistory.insertBefore(entry, this.chatHistory.firstChild);
        
        // Keep only last 10 entries
        while (this.chatHistory.children.length > 10) {
            this.chatHistory.removeChild(this.chatHistory.lastChild);
        }
    }
    
    playAudioResponse(audioUrl) {
        console.log('🔊 Playing audio response...');
        
        const audio = new Audio(audioUrl);
        audio.play().catch(error => {
            console.warn('🔇 Auto-play failed:', error);
            // Audio will still be available in the controls
        });
    }
    
    showError(message) {
        if (this.llmResult) {
            this.llmResult.innerHTML = `
                <div class="error-container">
                    <h4>❌ Error</h4>
                    <p>${message}</p>
                    <p><small>Please try again or check your microphone permissions.</small></p>
                </div>
            `;
        }
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
}

// Session ID Management (backward compatibility)
function setSessionId() {
    const sessionInput = document.getElementById('session-id');
    const sessionId = sessionInput.value.trim();
    
    if (sessionId) {
        console.log(`📋 Session ID set to: ${sessionId}`);
        document.querySelector('.status-message').textContent = `Session set: ${sessionId}`;
    } else {
        const newSessionId = 'session_' + Date.now();
        sessionInput.value = newSessionId;
        console.log(`🆕 Generated new session ID: ${newSessionId}`);
        document.querySelector('.status-message').textContent = `New session: ${newSessionId}`;
    }
    
    setTimeout(() => {
        document.querySelector('.status-message').textContent = 'Ready to listen';
    }, 2000);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Day 12: Modern Voice Assistant UI Loading...');
    
    // Initialize voice assistant
    window.voiceAssistant = new VoiceAssistant();
    
    // Set initial session ID
    const sessionInput = document.getElementById('session-id');
    if (sessionInput && !sessionInput.value) {
        sessionInput.value = 'session_' + Date.now();
    }
    
    console.log('✅ Voice Assistant Ready - Modern Single Button Interface');
});

// Expose for debugging
window.VoiceAssistant = VoiceAssistant;
