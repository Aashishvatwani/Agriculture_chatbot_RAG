import React, { useState } from 'react';
import './CartoonCompanions.css';

const CARTOONS = [
  {
    id: 'spuddy',
    name: 'Spuddy Spud',
    role: 'Chief Potato Officer 🥔',
    crop: 'Potato',
    sampleQuery: 'How do I prevent potato blight and improve yield?',
    quotes: [
      "I find your questions very a-peeling! 🥔",
      "I'm just a small fry with big farm dreams! 🍟",
      "Eyes on the crop! (Get it? Potato eyes? 👀)",
      "Bury your worries in well-drained loam! 🌱"
    ],
    renderSvg: (isDancing) => (
      <svg viewBox="0 0 100 110" className={`cartoon-character-svg ${isDancing ? 'dancing-spud' : ''}`}>
        <defs>
          <radialGradient id="spudGrad" cx="35%" cy="35%" r="65%">
            <stop offset="0%" stopColor="#fde047" />
            <stop offset="35%" stopColor="#d97706" />
            <stop offset="85%" stopColor="#92400e" />
            <stop offset="100%" stopColor="#78350f" />
          </radialGradient>
          <linearGradient id="bootGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#dc2626" />
            <stop offset="100%" stopColor="#991b1b" />
          </linearGradient>
        </defs>

        {/* Shadow */}
        <ellipse cx="50" cy="102" rx="28" ry="6" fill="rgba(0,0,0,0.2)" />

        {/* Little Red Rainboots */}
        <g className="spud-feet">
          <path d="M 32 90 L 32 99 C 32 102, 22 102, 22 99 L 26 90 Z" fill="url(#bootGrad)" />
          <path d="M 68 90 L 68 99 C 68 102, 78 102, 78 99 L 74 90 Z" fill="url(#bootGrad)" />
        </g>

        {/* Chunky Potato Body */}
        <path 
          d="M 50 18 
             C 75 16, 84 32, 85 52 
             C 86 72, 78 92, 50 94 
             C 22 92, 14 74, 15 52 
             C 16 30, 25 20, 50 18 Z" 
          fill="url(#spudGrad)" 
          stroke="#451a03" 
          strokeWidth="2.5" 
          className="potato-body"
        />

        {/* Potato Freckles / Spots */}
        <ellipse cx="30" cy="38" rx="2.5" ry="1.5" fill="#78350f" opacity="0.6" />
        <ellipse cx="72" cy="42" rx="3" ry="1.8" fill="#78350f" opacity="0.6" />
        <ellipse cx="36" cy="74" rx="2.2" ry="1.2" fill="#78350f" opacity="0.6" />
        <ellipse cx="68" cy="70" rx="3.5" ry="2" fill="#78350f" opacity="0.6" />

        {/* Little Arms */}
        <path d="M 16 54 Q 6 48 8 38" stroke="#78350f" strokeWidth="3" strokeLinecap="round" fill="none" className="left-arm" />
        <path d="M 84 54 Q 94 48 92 38" stroke="#78350f" strokeWidth="3" strokeLinecap="round" fill="none" className="right-arm" />

        {/* Big Cartoon Eyes */}
        <g className="spud-eyes">
          <ellipse cx="38" cy="48" rx="8" ry="10" fill="#ffffff" stroke="#451a03" strokeWidth="2" />
          <circle cx="40" cy="48" r="4.5" fill="#0f172a" />
          <circle cx="38" cy="45" r="2" fill="#ffffff" />

          <ellipse cx="62" cy="48" rx="8" ry="10" fill="#ffffff" stroke="#451a03" strokeWidth="2" />
          <circle cx="60" cy="48" r="4.5" fill="#0f172a" />
          <circle cx="58" cy="45" r="2" fill="#ffffff" />
        </g>

        {/* Rosy Cheeks */}
        <circle cx="28" cy="58" r="5" fill="#ef4444" opacity="0.45" />
        <circle cx="72" cy="58" r="5" fill="#ef4444" opacity="0.45" />

        {/* Cute Toothy Smile */}
        <path d="M 38 60 Q 50 74 62 60 Z" fill="#991b1b" stroke="#451a03" strokeWidth="2" />
        <rect x="47" y="60" width="6" height="4" rx="1" fill="#ffffff" />

        {/* Tiny Green Sprout on Head */}
        <path d="M 50 18 Q 44 8 36 10 Q 42 16 48 18" fill="#4ade80" stroke="#166534" strokeWidth="1.5" />
        <path d="M 50 18 Q 56 6 64 8 Q 58 15 52 18" fill="#22c55e" stroke="#166534" strokeWidth="1.5" />
      </svg>
    )
  },
  {
    id: 'cornelius',
    name: 'Cornelius',
    role: 'Director of A-MAIZE-ING 🌽',
    crop: 'Corn',
    sampleQuery: 'What is the optimal spacing and fertilizer for sweet corn?',
    quotes: [
      "You are absolute-stalk-ly A-MAIZE-ING! 🌽",
      "I'm all ears for your farming queries! 👂",
      "Careful now, don't butter me up! 🧈",
      "High nitrogen levels get me popping! 🍿"
    ],
    renderSvg: (isDancing) => (
      <svg viewBox="0 0 100 110" className={`cartoon-character-svg ${isDancing ? 'dancing-corn' : ''}`}>
        <defs>
          <linearGradient id="cornYellow" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#fef08a" />
            <stop offset="40%" stopColor="#facc15" />
            <stop offset="100%" stopColor="#eab308" />
          </linearGradient>
          <linearGradient id="huskGreen" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#4ade80" />
            <stop offset="100%" stopColor="#15803d" />
          </linearGradient>
        </defs>

        {/* Shadow */}
        <ellipse cx="50" cy="102" rx="26" ry="5.5" fill="rgba(0,0,0,0.2)" />

        {/* Little Dancing Feet */}
        <ellipse cx="40" cy="98" rx="6" ry="3.5" fill="#15803d" />
        <ellipse cx="60" cy="98" rx="6" ry="3.5" fill="#15803d" />

        {/* Corn Cob Body */}
        <path 
          d="M 50 16 
             C 66 18, 72 40, 70 76 
             C 68 94, 32 94, 30 76 
             C 28 40, 34 18, 50 16 Z" 
          fill="url(#cornYellow)" 
          stroke="#ca8a04" 
          strokeWidth="2.5" 
        />

        {/* Kernel Grid Texture */}
        <g stroke="#ca8a04" strokeWidth="1.2" opacity="0.45" fill="none">
          <path d="M 38 30 Q 50 33 62 30" />
          <path d="M 35 40 Q 50 44 65 40" />
          <path d="M 34 50 Q 50 55 66 50" />
          <path d="M 35 60 Q 50 66 65 60" />
          <path d="M 38 72 Q 50 77 62 72" />
          <path d="M 44 22 L 44 86" />
          <path d="M 50 20 L 50 88" />
          <path d="M 56 22 L 56 86" />
        </g>

        {/* Waving Husk Arms / Jacket */}
        <path 
          d="M 30 72 C 14 62, 8 40, 16 28 C 22 40, 24 60, 32 82 Z" 
          fill="url(#huskGreen)" 
          stroke="#166534" 
          strokeWidth="2" 
          className="left-husk"
        />
        <path 
          d="M 70 72 C 86 62, 92 40, 84 28 C 78 40, 76 60, 68 82 Z" 
          fill="url(#huskGreen)" 
          stroke="#166534" 
          strokeWidth="2" 
          className="right-husk"
        />

        {/* Corn Silk Hair */}
        <path d="M 45 16 Q 40 4 36 2 Q 44 8 48 16" fill="#fde047" stroke="#ca8a04" strokeWidth="1.5" />
        <path d="M 50 16 Q 52 2 56 0 Q 54 8 52 16" fill="#fde047" stroke="#ca8a04" strokeWidth="1.5" />
        <path d="M 53 16 Q 60 5 66 4 Q 58 10 54 16" fill="#fde047" stroke="#ca8a04" strokeWidth="1.5" />

        {/* Goofy Googly Eyes */}
        <ellipse cx="42" cy="44" rx="7.5" ry="9" fill="#ffffff" stroke="#713f12" strokeWidth="2" />
        <circle cx="44" cy="44" r="4.2" fill="#0f172a" />
        <circle cx="42" cy="42" r="1.8" fill="#ffffff" />

        <ellipse cx="58" cy="44" rx="7.5" ry="9" fill="#ffffff" stroke="#713f12" strokeWidth="2" />
        <circle cx="56" cy="44" r="4.2" fill="#0f172a" />
        <circle cx="54" cy="42" r="1.8" fill="#ffffff" />

        {/* Wide Grin with Buck Teeth */}
        <path d="M 38 58 Q 50 72 62 58 Z" fill="#991b1b" stroke="#713f12" strokeWidth="2" />
        <rect x="46" y="58" width="4" height="4.5" fill="#ffffff" stroke="#713f12" strokeWidth="0.8" />
        <rect x="50" y="58" width="4" height="4.5" fill="#ffffff" stroke="#713f12" strokeWidth="0.8" />
      </svg>
    )
  },
  {
    id: 'tommy',
    name: 'Tommy Tomato',
    role: 'Chief Nutrition Officer 🍅',
    crop: 'Tomato',
    sampleQuery: 'Why are my tomato leaves curling and turning yellow?',
    quotes: [
      "Catch-up with the latest agro-tech! (Ketchup!) 🥫",
      "I'm totally red-y for your crop queries! 🍅",
      "Don't squish me, I have sensitive skin! 🍅",
      "Calcium prevents blossom end rot — remember that! 🥛"
    ],
    renderSvg: (isDancing) => (
      <svg viewBox="0 0 100 110" className={`cartoon-character-svg ${isDancing ? 'dancing-tomato' : ''}`}>
        <defs>
          <radialGradient id="tomatoRed" cx="35%" cy="30%" r="70%">
            <stop offset="0%" stopColor="#fca5a5" />
            <stop offset="25%" stopColor="#ef4444" />
            <stop offset="70%" stopColor="#dc2626" />
            <stop offset="100%" stopColor="#991b1b" />
          </radialGradient>
        </defs>

        {/* Shadow */}
        <ellipse cx="50" cy="100" rx="30" ry="6" fill="rgba(0,0,0,0.2)" />

        {/* Round Tomato Body with Squash & Stretch */}
        <ellipse cx="50" cy="62" rx="36" ry="32" fill="url(#tomatoRed)" stroke="#7f1d1d" strokeWidth="2.5" className="tomato-body" />

        {/* Tomato Shine Highlights */}
        <ellipse cx="32" cy="44" rx="8" ry="4" transform="rotate(-30, 32, 44)" fill="rgba(255,255,255,0.4)" />

        {/* Big Star Calyx / Green Crown */}
        <g className="tomato-stem">
          <path d="M 50 32 L 48 18 Q 50 14 54 16 L 52 32 Z" fill="#15803d" stroke="#14532d" strokeWidth="1.5" />
          {/* Leaves of star */}
          <polygon points="50,32 30,28 42,36 28,42 44,40 50,42 56,40 72,42 58,36 70,28" fill="#22c55e" stroke="#15803d" strokeWidth="1.5" />
        </g>

        {/* Big Anime Eyes */}
        <g className="tomato-eyes">
          <circle cx="37" cy="58" r="8" fill="#0f172a" />
          <circle cx="34" cy="55" r="3.2" fill="#ffffff" />
          <circle cx="39" cy="61" r="1.5" fill="#ffffff" />

          <circle cx="63" cy="58" r="8" fill="#0f172a" />
          <circle cx="60" cy="55" r="3.2" fill="#ffffff" />
          <circle cx="65" cy="61" r="1.5" fill="#ffffff" />
        </g>

        {/* Rosy Blushing Cheeks */}
        <ellipse cx="25" cy="66" rx="6" ry="4" fill="#fb7185" opacity="0.7" />
        <ellipse cx="75" cy="66" rx="6" ry="4" fill="#fb7185" opacity="0.7" />

        {/* Happy Open Smile */}
        <path d="M 40 68 Q 50 82 60 68 Z" fill="#581c87" stroke="#7f1d1d" strokeWidth="2" />
        <path d="M 44 74 Q 50 80 56 74" fill="#f43f5e" />

        {/* Cute Little White Gloves Waving */}
        <g className="tomato-hands">
          <circle cx="12" cy="64" r="5" fill="#ffffff" stroke="#7f1d1d" strokeWidth="1.5" />
          <circle cx="88" cy="64" r="5" fill="#ffffff" stroke="#7f1d1d" strokeWidth="1.5" />
        </g>
      </svg>
    )
  },
  {
    id: 'carrotina',
    name: 'Carrotina',
    role: 'Root Systems Specialist 🥕',
    crop: 'Carrot',
    sampleQuery: 'What soil texture is best for deep carrot root development?',
    quotes: [
      "24-carrot intelligence right here! 💎🥕",
      "I don't carrot all about pesky weeds! 🕶️",
      "Keep calm and carrot on! ✨",
      "Loose, sandy loam is my favorite playground! 🏖️"
    ],
    renderSvg: (isDancing) => (
      <svg viewBox="0 0 100 110" className={`cartoon-character-svg ${isDancing ? 'dancing-carrot' : ''}`}>
        <defs>
          <linearGradient id="carrotGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#fdba74" />
            <stop offset="40%" stopColor="#f97316" />
            <stop offset="100%" stopColor="#c2410c" />
          </linearGradient>
        </defs>

        {/* Shadow */}
        <ellipse cx="50" cy="102" rx="18" ry="4.5" fill="rgba(0,0,0,0.2)" />

        {/* Bushy Green Fronds / Hair */}
        <g className="carrot-greens">
          <path d="M 50 26 Q 34 10 24 16 Q 36 22 46 28" fill="#4ade80" stroke="#15803d" strokeWidth="1.5" />
          <path d="M 50 26 Q 50 4 48 0 Q 54 8 52 26" fill="#22c55e" stroke="#15803d" strokeWidth="1.5" />
          <path d="M 50 26 Q 66 10 76 16 Q 64 22 54 28" fill="#4ade80" stroke="#15803d" strokeWidth="1.5" />
        </g>

        {/* Tapered Carrot Body */}
        <path 
          d="M 32 30 
             Q 50 26 68 30 
             Q 66 60 54 98 
             Q 50 102 46 98 
             Q 34 60 32 30 Z" 
          fill="url(#carrotGrad)" 
          stroke="#9a3412" 
          strokeWidth="2.5" 
          className="carrot-body"
        />

        {/* Carrot Ring Textures */}
        <g stroke="#9a3412" strokeWidth="1.2" opacity="0.4" fill="none">
          <path d="M 36 38 Q 44 42 48 38" />
          <path d="M 52 48 Q 58 52 64 48" />
          <path d="M 38 60 Q 46 64 52 60" />
          <path d="M 44 76 Q 50 80 56 76" />
        </g>

        {/* Cool Sunglasses */}
        <g className="carrot-shades">
          <rect x="34" y="42" width="13" height="9" rx="2" fill="#0f172a" />
          <rect x="53" y="42" width="13" height="9" rx="2" fill="#0f172a" />
          <line x1="47" y1="46" x2="53" y2="46" stroke="#0f172a" strokeWidth="2.5" />
          {/* Glare line */}
          <line x1="36" y1="44" x2="44" y2="49" stroke="#60a5fa" strokeWidth="1.2" />
          <line x1="55" y1="44" x2="63" y2="49" stroke="#60a5fa" strokeWidth="1.2" />
        </g>

        {/* Smirk Smile */}
        <path d="M 44 58 Q 52 64 58 57" stroke="#9a3412" strokeWidth="2.5" strokeLinecap="round" fill="none" />
      </svg>
    )
  },
  {
    id: 'buzzy',
    name: 'Buzzy Bee',
    role: 'Chief Pollinator 🐝',
    crop: 'Pollination',
    sampleQuery: 'How do honeybees and pollinators increase fruit set and yield?',
    quotes: [
      "Bee-lieve in organic farming! 🐝",
      "Buzzing with 10,000 agricultural facts! 🍯",
      "Protect your pollinators from harsh pesticides! 🌸",
      "I give this farm query an A-Plus-Honey! 🍯✨"
    ],
    renderSvg: (isDancing) => (
      <svg viewBox="0 0 100 110" className={`cartoon-character-svg ${isDancing ? 'dancing-bee' : ''}`}>
        <defs>
          <linearGradient id="beeYellow" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#fef08a" />
            <stop offset="50%" stopColor="#facc15" />
            <stop offset="100%" stopColor="#eab308" />
          </linearGradient>
          <linearGradient id="wingGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="rgba(255,255,255,0.9)" />
            <stop offset="100%" stopColor="rgba(191,219,254,0.4)" />
          </linearGradient>
        </defs>

        {/* Flapping Wings */}
        <g className="bee-wings">
          <ellipse cx="36" cy="32" rx="16" ry="10" transform="rotate(-30, 36, 32)" fill="url(#wingGrad)" stroke="#93c5fd" strokeWidth="1.5" />
          <ellipse cx="64" cy="32" rx="16" ry="10" transform="rotate(30, 64, 32)" fill="url(#wingGrad)" stroke="#93c5fd" strokeWidth="1.5" />
        </g>

        {/* Striped Bee Body */}
        <ellipse cx="50" cy="58" rx="28" ry="24" fill="url(#beeYellow)" stroke="#713f12" strokeWidth="2.5" />

        {/* Black Stripes */}
        <path d="M 38 38 C 42 42, 42 74, 38 78 L 46 79 C 50 75, 50 41, 46 37 Z" fill="#1e293b" />
        <path d="M 54 37 C 58 41, 58 75, 54 79 L 62 78 C 66 74, 66 42, 62 38 Z" fill="#1e293b" />

        {/* Stinger */}
        <polygon points="78,58 86,58 78,62" fill="#0f172a" />

        {/* Cute Flying Goggles / Eyes */}
        <g className="bee-goggles">
          <circle cx="34" cy="54" r="8" fill="#e0f2fe" stroke="#0f172a" strokeWidth="2" />
          <circle cx="35" cy="54" r="4" fill="#0f172a" />
          <circle cx="33" cy="52" r="1.5" fill="#ffffff" />

          <circle cx="50" cy="54" r="8" fill="#e0f2fe" stroke="#0f172a" strokeWidth="2" />
          <circle cx="51" cy="54" r="4" fill="#0f172a" />
          <circle cx="49" cy="52" r="1.5" fill="#ffffff" />
        </g>

        {/* Antennae */}
        <path d="M 28 42 Q 22 30 18 32" stroke="#0f172a" strokeWidth="2" fill="none" />
        <circle cx="18" cy="32" r="2.5" fill="#eab308" />

        <path d="M 36 40 Q 32 26 28 28" stroke="#0f172a" strokeWidth="2" fill="none" />
        <circle cx="28" cy="28" r="2.5" fill="#eab308" />

        {/* Happy smile */}
        <path d="M 36 65 Q 42 72 48 65" stroke="#713f12" strokeWidth="2" strokeLinecap="round" fill="none" />
      </svg>
    )
  }
];

export default function CartoonCompanions({ onSelectQuery }) {
  const [activeSpeech, setActiveSpeech] = useState(null);
  const [dancingId, setDancingId] = useState(null);

  const handleCartoonClick = (cartoon) => {
    // Pick a random quote
    const randomQuote = cartoon.quotes[Math.floor(Math.random() * cartoon.quotes.length)];
    setActiveSpeech({
      id: cartoon.id,
      name: cartoon.name,
      quote: randomQuote,
      sampleQuery: cartoon.sampleQuery,
    });

    // Trigger dancing physics
    setDancingId(cartoon.id);
    setTimeout(() => setDancingId(null), 1200);
  };

  const handleAskQuery = (query) => {
    if (onSelectQuery) {
      onSelectQuery(query);
      setActiveSpeech(null);
    }
  };

  return (
    <div className="cartoon-companions-bar">
      <div className="companions-header">
        <span className="companions-badge">🌾 Farm Crew Companions</span>
        <span className="companions-hint">Click any friend for farm wisdom & jokes!</span>
      </div>

      <div className="companions-grid">
        {CARTOONS.map((c) => {
          const isDancing = dancingId === c.id;
          const isActive = activeSpeech && activeSpeech.id === c.id;

          return (
            <div
              key={c.id}
              className={`cartoon-card ${isActive ? 'active-companion' : ''}`}
              onClick={() => handleCartoonClick(c)}
              title={`Click to talk with ${c.name}!`}
            >
              <div className="cartoon-svg-wrapper">
                {c.renderSvg(isDancing)}
              </div>
              <div className="cartoon-info">
                <span className="cartoon-name">{c.name}</span>
                <span className="cartoon-role">{c.crop}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Floating Cartoon Speech Bubble */}
      {activeSpeech && (
        <div className="cartoon-speech-bubble">
          <div className="bubble-tail"></div>
          <div className="bubble-header">
            <strong>{activeSpeech.name} says:</strong>
            <button 
              className="bubble-close" 
              onClick={(e) => { e.stopPropagation(); setActiveSpeech(null); }}
            >
              ✕
            </button>
          </div>
          <p className="bubble-quote">"{activeSpeech.quote}"</p>
          <div className="bubble-actions">
            <button 
              className="bubble-ask-btn"
              onClick={() => handleAskQuery(activeSpeech.sampleQuery)}
            >
              🌱 Ask: "{activeSpeech.sampleQuery}"
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
