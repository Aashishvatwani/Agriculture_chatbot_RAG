import { useState, useRef, useEffect } from 'react';
import './AgriSearchBot.css';
import ChatMessage from './ChatMessage';
import BotMascot from './BotMascot';
import FeaturePanel from './FeaturePanel';
import VoiceInput from './VoiceInput';
import ImageFeatures from './ImageFeatures';

function AgriSearchBot() {
  const [messages, setMessages] = useState(() => {
    const saved = localStorage.getItem('chat_messages');
    if (saved) {
      return JSON.parse(saved);
    }
    return [
      {
        id: 1,
        type: 'bot',
        content: 'Welcome to AgriSearch Bot! 🌱 I\'m your AI-powered agriculture and forestry intelligence assistant. How can I help you today?',
        timestamp: new Date(),
      }
    ];
  });
  const [inputValue, setInputValue] = useState('');
  const [selectedImage, setSelectedImage] = useState(null); // Base64 image
  const [isTyping, setIsTyping] = useState(false);
  const [showBot, setShowBot] = useState(false);
  const [showFeatures, setShowFeatures] = useState(true);
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);

  useEffect(() => {
    // Entry animation
    setTimeout(() => setShowBot(true), 300);
  }, []);

  useEffect(() => {
    scrollToBottom();
    // Persist messages to localStorage whenever they change
    localStorage.setItem('chat_messages', JSON.stringify(messages));
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const newMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      image: selectedImage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, newMessage]);
    const userQuery = inputValue;
    setInputValue('');
    setIsTyping(true);
    setShowFeatures(false);

    // Call backend API
    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userQuery,
          image: selectedImage, // Send base64 image if selected
          session_id: null
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get response from server');
      }

      const data = await response.json();
      
      const botResponse = {
        id: Date.now(),
        type: 'bot',
        content: data.response,
        richContent: data.richContent,
        sources: data.sources, // Pass sources
        timestamp: new Date(),
      };
      
      if (selectedImage) {
        setSelectedImage(null);
      }

      setMessages(prev => [...prev, botResponse]);
      setIsTyping(false);
    } catch (error) {
      console.error('Error calling backend:', error);
      
      // Fallback to simulated response
      const botResponse = generateBotResponse(userQuery);
      setMessages(prev => [...prev, botResponse]);
      setIsTyping(false);
    }
  };

  const generateBotResponse = (userInput) => {
    const input = userInput.toLowerCase();
    let content = '';
    let richContent = null;

    if (input.includes('disease') || input.includes('crop')) {
      content = 'I can help you identify crop diseases. Here are some common issues:';
      richContent = {
        type: 'disease-card',
        data: [
          { name: 'Leaf Blight', severity: 'High', treatment: 'Apply fungicide' },
          { name: 'Root Rot', severity: 'Medium', treatment: 'Improve drainage' },
        ]
      };
    } else if (input.includes('soil') || input.includes('health')) {
      content = 'Soil health is crucial for optimal growth. Here\'s what I found:';
      richContent = {
        type: 'soil-card',
        data: {
          pH: 6.5,
          nitrogen: 'Medium',
          phosphorus: 'High',
          potassium: 'Low',
          recommendation: 'Add potassium-rich fertilizer'
        }
      };
    } else if (input.includes('weather') || input.includes('forecast')) {
      content = 'Here\'s the agricultural weather forecast:';
      richContent = {
        type: 'weather-card',
        data: {
          temperature: '28°C',
          humidity: '65%',
          rainfall: '12mm expected',
          recommendation: 'Good conditions for irrigation'
        }
      };
    } else if (input.includes('fertilizer') || input.includes('nutrient')) {
      content = 'Based on your soil analysis, here are my fertilizer recommendations:';
      richContent = {
        type: 'fertilizer-card',
        data: {
          npk: '10-26-26',
          amount: '150 kg/hectare',
          timing: 'Apply before monsoon',
          cost: '₹2,400'
        }
      };
    } else {
      content = 'I can assist you with crop disease detection, soil health analysis, weather alerts, fertilizer recommendations, and forestry management. What would you like to know more about?';
    }

    return {
      id: Date.now(),
      type: 'bot',
      content,
      richContent,
      timestamp: new Date(),
    };
  };

  const handleVoiceInput = (transcript) => {
    setInputValue(transcript);
  };

  const handleFeatureSelect = (featureQuery) => {
    setInputValue(featureQuery);
    setShowFeatures(false);
  };

  return (
    <div className={`agrisearch-container ${showBot ? 'show' : ''}`}>
      {/* Animated Background */}
      <div className="animated-background">
        <div className="floating-leaf leaf-1"></div>
        <div className="floating-leaf leaf-2"></div>
        <div className="floating-leaf leaf-3"></div>
        <div className="floating-leaf leaf-4"></div>
        <div className="glow-orb orb-1"></div>
        <div className="glow-orb orb-2"></div>
      </div>

      {/* Main Chat Container */}
      <div className="chat-container">
        {/* Header */}
        <div className="chat-header">
          <BotMascot isTyping={isTyping} />
          <div className="header-content">
            <h1 className="bot-title">AgriSearch Bot</h1>
            <p className="bot-subtitle">AI-Powered Agriculture & Forestry Intelligence</p>
          </div>
          <div className="header-actions">
            <button className="icon-btn" title="Settings">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M10 12.5C11.3807 12.5 12.5 11.3807 12.5 10C12.5 8.61929 11.3807 7.5 10 7.5C8.61929 7.5 7.5 8.61929 7.5 10C7.5 11.3807 8.61929 12.5 10 12.5Z" stroke="currentColor" strokeWidth="1.5"/>
                <path d="M16.25 10C16.25 10.625 16.125 11.125 15.875 11.625L17.5 13.25L15.875 16.25L13.625 15.375C13 15.875 12.25 16.125 11.5 16.25V18.75H8.5V16.25C7.75 16.125 7 15.875 6.375 15.375L4.125 16.25L2.5 13.25L4.125 11.625C3.875 11.125 3.75 10.625 3.75 10C3.75 9.375 3.875 8.875 4.125 8.375L2.5 6.75L4.125 3.75L6.375 4.625C7 4.125 7.75 3.875 8.5 3.75V1.25H11.5V3.75C12.25 3.875 13 4.125 13.625 4.625L15.875 3.75L17.5 6.75L15.875 8.375C16.125 8.875 16.25 9.375 16.25 10Z" stroke="currentColor" strokeWidth="1.5"/>
              </svg>
            </button>
          </div>
        </div>

        {/* Messages Area */}
        <div className="messages-container" ref={chatContainerRef}>
          {/* Feature Panel Overlay */}
          {showFeatures && messages.length === 1 && (
            <FeaturePanel onFeatureSelect={handleFeatureSelect} />
          )}
          
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
          {isTyping && (
            <div className="typing-indicator">
              <div className="bot-avatar-small">
                <div className="leaf-icon">🍃</div>
              </div>
              <div className="typing-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="input-container">
          <form onSubmit={handleSendMessage} className="input-form">
            <div className="input-wrapper">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Ask about crops, soil, weather, forestry..."
                className="chat-input"
              />
              <VoiceInput onTranscript={handleVoiceInput} />
              <ImageFeatures 
                onImageSelect={setSelectedImage} 
                selectedImage={selectedImage}
                disabled={isTyping} 
              />
              <button type="submit" className="send-btn" disabled={!inputValue.trim() && !selectedImage}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
            </div>
          </form>
          <div className="input-footer">
            <span className="footer-text">🌿 Powered by AI • Nature-Inspired Intelligence</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AgriSearchBot;
