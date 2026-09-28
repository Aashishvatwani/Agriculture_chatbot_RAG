import React, { useState, useEffect } from 'react';
import './CartoonAvatar.css';

export function BotCartoonAvatar({ isTyping = false }) {
  const [blink, setBlink] = useState(false);
  const [expression, setExpression] = useState('happy'); // 'happy', 'wink', 'derp'

  useEffect(() => {
    const blinkTimer = setInterval(() => {
      setBlink(true);
      setTimeout(() => setBlink(false), 180);
    }, 2800 + Math.random() * 2000);

    return () => clearInterval(blinkTimer);
  }, []);

  const handleClick = () => {
    const expressions = ['happy', 'wink', 'surprised', 'cool'];
    const next = expressions[(expressions.indexOf(expression) + 1) % expressions.length];
    setExpression(next);
  };

  return (
    <div 
      className={`cartoon-avatar bot-avatar-cartoon ${isTyping ? 'typing-bounce' : ''}`}
      onClick={handleClick}
      title="Click me for a funny face!"
    >
      <svg viewBox="0 0 100 100" className="avatar-svg">
        <defs>
          <radialGradient id="sproutGrad" cx="40%" cy="35%" r="60%">
            <stop offset="0%" stopColor="#86efac" />
            <stop offset="65%" stopColor="#22c55e" />
            <stop offset="100%" stopColor="#15803d" />
          </radialGradient>
          <radialGradient id="hatGrad" cx="30%" cy="30%" r="70%">
            <stop offset="0%" stopColor="#fef08a" />
            <stop offset="80%" stopColor="#eab308" />
            <stop offset="100%" stopColor="#ca8a04" />
          </radialGradient>
          <linearGradient id="leafGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#bbf7d0" />
            <stop offset="100%" stopColor="#16a34a" />
          </linearGradient>
        </defs>

        {/* Shadow */}
        <ellipse cx="50" cy="92" rx="30" ry="6" fill="rgba(0,0,0,0.18)" />

        {/* Wiggling Top Sprout Leaves */}
        <g className="top-sprout">
          <path 
            d="M 50 30 C 45 15, 30 12, 28 20 C 26 28, 42 28, 50 32 Z" 
            fill="url(#leafGrad)" 
            className="leaf-left"
          />
          <path 
            d="M 50 30 C 55 12, 72 10, 74 18 C 76 26, 58 28, 50 32 Z" 
            fill="url(#leafGrad)" 
            className="leaf-right"
          />
          <circle cx="50" cy="30" r="3" fill="#15803d" />
        </g>

        {/* Round Sprout Body */}
        <ellipse cx="50" cy="62" rx="36" ry="32" fill="url(#sproutGrad)" stroke="#166534" strokeWidth="2.5" />

        {/* Rosy Cheeks */}
        <ellipse cx="28" cy="68" rx="6" ry="3.5" fill="#f87171" opacity="0.6" />
        <ellipse cx="72" cy="68" rx="6" ry="3.5" fill="#f87171" opacity="0.6" />

        {/* Eyes based on expression & blink */}
        {blink ? (
          <g stroke="#14532d" strokeWidth="3" strokeLinecap="round" fill="none">
            <path d="M 33 58 Q 40 64 47 58" />
            <path d="M 53 58 Q 60 64 67 58" />
          </g>
        ) : expression === 'wink' ? (
          <g>
            {/* Left Eye Open */}
            <circle cx="40" cy="58" r="6.5" fill="#0f172a" />
            <circle cx="38" cy="56" r="2.5" fill="#ffffff" />
            <circle cx="42" cy="60" r="1.2" fill="#ffffff" />
            {/* Right Eye Winking */}
            <path d="M 54 58 Q 61 64 68 58" stroke="#14532d" strokeWidth="3" strokeLinecap="round" fill="none" />
          </g>
        ) : expression === 'cool' ? (
          /* Sunglasses */
          <g className="cool-shades">
            <rect x="28" y="52" width="20" height="12" rx="3" fill="#1e293b" />
            <rect x="52" y="52" width="20" height="12" rx="3" fill="#1e293b" />
            <line x1="48" y1="58" x2="52" y2="58" stroke="#0f172a" strokeWidth="2.5" />
            <line x1="28" y1="55" x2="48" y2="61" stroke="rgba(255,255,255,0.4)" strokeWidth="1.5" />
            <line x1="52" y1="55" x2="72" y2="61" stroke="rgba(255,255,255,0.4)" strokeWidth="1.5" />
          </g>
        ) : expression === 'surprised' ? (
          <g>
            <circle cx="40" cy="56" r="7" fill="#0f172a" />
            <circle cx="38" cy="54" r="3" fill="#ffffff" />
            <circle cx="60" cy="56" r="7" fill="#0f172a" />
            <circle cx="58" cy="54" r="3" fill="#ffffff" />
          </g>
        ) : (
          /* Normal Cute Big Eyes */
          <g className="cute-eyes">
            <circle cx="40" cy="58" r="6.5" fill="#0f172a" />
            <circle cx="38" cy="56" r="2.5" fill="#ffffff" />
            <circle cx="42" cy="60" r="1.2" fill="#ffffff" />

            <circle cx="60" cy="58" r="6.5" fill="#0f172a" />
            <circle cx="58" cy="56" r="2.5" fill="#ffffff" />
            <circle cx="62" cy="60" r="1.2" fill="#ffffff" />
          </g>
        )}

        {/* Mouth */}
        {expression === 'surprised' ? (
          <ellipse cx="50" cy="74" rx="4" ry="6" fill="#991b1b" stroke="#14532d" strokeWidth="1.5" />
        ) : expression === 'cool' ? (
          <path d="M 44 72 Q 50 78 58 72" stroke="#14532d" strokeWidth="2.5" strokeLinecap="round" fill="none" />
        ) : (
          <path d="M 43 70 Q 50 78 57 70 Z" fill="#b91c1c" stroke="#14532d" strokeWidth="1.5" />
        )}

        {/* Tiny farmer hat tilted */}
        <g className="farmer-hat" transform="translate(42, 22) rotate(15)">
          <ellipse cx="15" cy="12" rx="18" ry="4" fill="url(#hatGrad)" stroke="#854d0e" strokeWidth="1" />
          <path d="M 7 12 C 7 3, 23 3, 23 12 Z" fill="url(#hatGrad)" stroke="#854d0e" strokeWidth="1" />
          <rect x="7" y="10" width="16" height="2.5" fill="#dc2626" />
        </g>
      </svg>
    </div>
  );
}

export function UserCartoonAvatar() {
  const [blink, setBlink] = useState(false);

  useEffect(() => {
    const blinkTimer = setInterval(() => {
      setBlink(true);
      setTimeout(() => setBlink(false), 180);
    }, 3200 + Math.random() * 2500);

    return () => clearInterval(blinkTimer);
  }, []);

  return (
    <div className="cartoon-avatar user-avatar-cartoon" title="Happy Farmer!">
      <svg viewBox="0 0 100 100" className="avatar-svg">
        <defs>
          <radialGradient id="faceGrad" cx="40%" cy="40%" r="60%">
            <stop offset="0%" stopColor="#fed7aa" />
            <stop offset="100%" stopColor="#fba765" />
          </radialGradient>
          <linearGradient id="strawGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#fef08a" />
            <stop offset="50%" stopColor="#facc15" />
            <stop offset="100%" stopColor="#ca8a04" />
          </linearGradient>
          <linearGradient id="shirtGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#60a5fa" />
            <stop offset="100%" stopColor="#2563eb" />
          </linearGradient>
        </defs>

        {/* Overalls / Shoulders */}
        <path d="M 20 85 C 20 74, 30 72, 50 72 C 70 72, 80 74, 80 85 L 85 100 L 15 100 Z" fill="url(#shirtGrad)" />
        {/* Overalls Straps */}
        <rect x="30" y="72" width="7" height="28" fill="#1d4ed8" rx="2" />
        <rect x="63" y="72" width="7" height="28" fill="#1d4ed8" rx="2" />
        <circle cx="33.5" cy="78" r="2" fill="#fbbf24" />
        <circle cx="66.5" cy="78" r="2" fill="#fbbf24" />

        {/* Red Bandana in neck */}
        <polygon points="45,72 55,72 50,80" fill="#ef4444" />

        {/* Face */}
        <circle cx="50" cy="56" r="24" fill="url(#faceGrad)" stroke="#c2410c" strokeWidth="1.5" />

        {/* Rosy Cheeks */}
        <circle cx="34" cy="62" r="4.5" fill="#f87171" opacity="0.6" />
        <circle cx="66" cy="62" r="4.5" fill="#f87171" opacity="0.6" />

        {/* Cheerful Freckles */}
        <circle cx="36" cy="58" r="0.8" fill="#c2410c" />
        <circle cx="39" cy="59" r="0.8" fill="#c2410c" />
        <circle cx="61" cy="59" r="0.8" fill="#c2410c" />
        <circle cx="64" cy="58" r="0.8" fill="#c2410c" />

        {/* Eyes */}
        {blink ? (
          <g stroke="#7c2d12" strokeWidth="2.5" strokeLinecap="round" fill="none">
            <path d="M 37 54 Q 42 58 47 54" />
            <path d="M 53 54 Q 58 58 63 54" />
          </g>
        ) : (
          <g>
            <circle cx="42" cy="53" r="4.5" fill="#0f172a" />
            <circle cx="40.5" cy="51.5" r="1.8" fill="#ffffff" />
            <circle cx="58" cy="53" r="4.5" fill="#0f172a" />
            <circle cx="56.5" cy="51.5" r="1.8" fill="#ffffff" />
          </g>
        )}

        {/* Happy Smile with dimples */}
        <path d="M 42 63 Q 50 71 58 63" stroke="#7c2d12" strokeWidth="2.5" strokeLinecap="round" fill="none" />
        <path d="M 40 61 L 41 63" stroke="#7c2d12" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M 60 61 L 59 63" stroke="#7c2d12" strokeWidth="1.5" strokeLinecap="round" />

        {/* Big Straw Farmer Hat */}
        <g className="straw-hat">
          {/* Hat Crown */}
          <path d="M 30 38 C 30 18, 70 18, 70 38 Z" fill="url(#strawGrad)" stroke="#a16207" strokeWidth="1.5" />
          {/* Hat Ribbon */}
          <path d="M 29 36 C 40 33, 60 33, 71 36 L 71 40 C 60 37, 40 37, 29 40 Z" fill="#15803d" />
          {/* Hat Brim */}
          <ellipse cx="50" cy="40" rx="38" ry="10" fill="url(#strawGrad)" stroke="#a16207" strokeWidth="1.5" />
          {/* Straw Texture details */}
          <line x1="40" y1="23" x2="42" y2="34" stroke="#a16207" strokeWidth="1" opacity="0.4" />
          <line x1="50" y1="21" x2="50" y2="34" stroke="#a16207" strokeWidth="1" opacity="0.4" />
          <line x1="60" y1="23" x2="58" y2="34" stroke="#a16207" strokeWidth="1" opacity="0.4" />
          {/* Little wheat stalk in hat */}
          <path d="M 66 38 Q 78 26 84 20" stroke="#ca8a04" strokeWidth="1.8" fill="none" />
          <ellipse cx="80" cy="22" rx="2" ry="4" transform="rotate(30, 80, 22)" fill="#facc15" />
          <ellipse cx="83" cy="20" rx="2" ry="4" transform="rotate(45, 83, 20)" fill="#facc15" />
        </g>
      </svg>
    </div>
  );
}
