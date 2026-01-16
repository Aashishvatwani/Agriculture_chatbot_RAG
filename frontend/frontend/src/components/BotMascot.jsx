import { useEffect, useState } from 'react';
import './BotMascot.css';

function BotMascot({ isTyping }) {
  const [blink, setBlink] = useState(false);

  useEffect(() => {
    // Random blink animation
    const blinkInterval = setInterval(() => {
      setBlink(true);
      setTimeout(() => setBlink(false), 200);
    }, 3000 + Math.random() * 2000);

    return () => clearInterval(blinkInterval);
  }, []);

  return (
    <div className={`bot-mascot ${isTyping ? 'typing' : ''}`}>
      <div className="mascot-container">
        {/* Glowing Aura */}
        <div className="glow-aura"></div>
        
        {/* Main Leaf Body */}
        <div className="leaf-body">
          <div className="leaf-veins">
            <div className="vein central-vein"></div>
            <div className="vein side-vein vein-1"></div>
            <div className="vein side-vein vein-2"></div>
            <div className="vein side-vein vein-3"></div>
            <div className="vein side-vein vein-4"></div>
          </div>
          
          {/* Circuit-like patterns */}
          <div className="circuit-patterns">
            <div className="circuit-dot dot-1"></div>
            <div className="circuit-dot dot-2"></div>
            <div className="circuit-dot dot-3"></div>
            <div className="circuit-line line-1"></div>
            <div className="circuit-line line-2"></div>
          </div>

          {/* Eyes */}
          <div className="eyes">
            <div className={`eye left-eye ${blink ? 'blink' : ''}`}>
              <div className="pupil"></div>
              <div className="eye-shine"></div>
            </div>
            <div className={`eye right-eye ${blink ? 'blink' : ''}`}>
              <div className="pupil"></div>
              <div className="eye-shine"></div>
            </div>
          </div>

          {/* Smile */}
          <div className="smile"></div>
        </div>

        {/* Floating Particles */}
        <div className="particles">
          <div className="particle particle-1">✨</div>
          <div className="particle particle-2">🌿</div>
          <div className="particle particle-3">✨</div>
        </div>

        {/* Root-like tendrils */}
        <div className="tendrils">
          <div className="tendril tendril-1"></div>
          <div className="tendril tendril-2"></div>
          <div className="tendril tendril-3"></div>
        </div>
      </div>
    </div>
  );
}

export default BotMascot;
