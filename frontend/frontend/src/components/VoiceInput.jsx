import { useState, useEffect, useRef } from 'react';
import './VoiceInput.css';

const VoiceInput = ({ onTranscript }) => {
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  useEffect(() => {
    // 1. Check browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.warn("Browser does not support Speech Recognition");
      return;
    }

    // 2. Setup Recognition
    const recognition = new SpeechRecognition();
    recognition.continuous = true;      // Keep listening even if user pauses
    recognition.interimResults = true;  // Show results while talking? (False means only final)
    recognition.lang = 'en-US';         // Set language

    // 3. Handle Results
    recognition.onresult = (event) => {
      let finalTranscript = '';
      
      // Loop through results (there might be multiple chunks)
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript + ' ';
        }
      }

      if (finalTranscript) {
        onTranscript(finalTranscript.trim());
      }
    };

    // Handle Errors
    recognition.onerror = (event) => {
      console.error("Speech recognition error", event.error);
      setIsListening(false);
    };

    // Handle End (e.g. if silence stops it automatically)
    recognition.onend = () => {
      // Optional: Auto-restart if you want "always on", otherwise just update state
      setIsListening(false);
    };

    recognitionRef.current = recognition;
  }, [onTranscript]);

  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert("Speech recognition not supported in this browser.");
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  return (
    <button
      type="button"
      className={`voice-btn ${isListening ? 'listening' : ''}`}
      onClick={toggleListening}
      title="Voice Input"
    >
      {/* Your SVG Icon */}
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path d="M10 1.25C8.27411 1.25 6.875 2.64911 6.875 4.375V10C6.875 11.7259 8.27411 13.125 10 13.125C11.7259 13.125 13.125 11.7259 13.125 10V4.375C13.125 2.64911 11.7259 1.25 10 1.25Z" stroke="currentColor" strokeWidth="1.5" />
        <path d="M4.375 8.75V10C4.375 13.1066 6.89339 15.625 10 15.625C13.1066 15.625 15.625 13.1066 15.625 10V8.75" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M10 15.625V18.75" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M7.5 18.75H12.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
      
      {isListening && (
        <div className="voice-waves">
          <span className="wave wave-1"></span>
          <span className="wave wave-2"></span>
          <span className="wave wave-3"></span>
        </div>
      )}
    </button>
  );
};

export default VoiceInput;