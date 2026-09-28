import React from 'react';
import './CartoonBackground.css';

export default function CartoonBackground() {
  return (
    <div className="cartoon-ambient-background" aria-hidden="true">
      {/* 1. Cool Cartoon Sun in corner */}
      <div className="cartoon-sun">
        <svg viewBox="0 0 100 100" className="sun-svg">
          <circle cx="50" cy="50" r="28" fill="#facc15" stroke="#eab308" strokeWidth="2.5" />
          {/* Sun Rays */}
          <g className="sun-rays" stroke="#f59e0b" strokeWidth="3" strokeLinecap="round">
            <line x1="50" y1="12" x2="50" y2="4" />
            <line x1="50" y1="88" x2="50" y2="96" />
            <line x1="12" y1="50" x2="4" y2="50" />
            <line x1="88" y1="50" x2="96" y2="50" />
            <line x1="24" y1="24" x2="18" y2="18" />
            <line x1="76" y1="76" x2="82" y2="82" />
            <line x1="24" y1="76" x2="18" y2="82" />
            <line x1="76" y1="24" x2="82" y2="18" />
          </g>
          {/* Cool Sunglasses */}
          <rect x="32" y="44" width="16" height="10" rx="3" fill="#1e293b" />
          <rect x="52" y="44" width="16" height="10" rx="3" fill="#1e293b" />
          <line x1="48" y1="48" x2="52" y2="48" stroke="#0f172a" strokeWidth="3" />
          <line x1="34" y1="46" x2="44" y2="52" stroke="rgba(255,255,255,0.6)" strokeWidth="1.5" />
          <line x1="54" y1="46" x2="64" y2="52" stroke="rgba(255,255,255,0.6)" strokeWidth="1.5" />
          {/* Confident Smirk */}
          <path d="M 44 60 Q 52 66 60 59" stroke="#78350f" strokeWidth="2" strokeLinecap="round" fill="none" />
        </svg>
      </div>

      {/* 2. Floating Parachute Potato */}
      <div className="floating-chute-spud">
        <svg viewBox="0 0 80 120" className="chute-svg">
          {/* Parachute Leaf Canopy */}
          <path d="M 10 38 Q 40 4 70 38 Q 40 32 10 38 Z" fill="#22c55e" stroke="#15803d" strokeWidth="1.8" />
          {/* Strings */}
          <line x1="12" y1="38" x2="38" y2="70" stroke="rgba(255,255,255,0.4)" strokeWidth="1.2" />
          <line x1="68" y1="38" x2="42" y2="70" stroke="rgba(255,255,255,0.4)" strokeWidth="1.2" />
          <line x1="40" y1="34" x2="40" y2="70" stroke="rgba(255,255,255,0.4)" strokeWidth="1.2" />
          {/* Little Spud with Goggles */}
          <ellipse cx="40" cy="80" rx="14" ry="12" fill="#d97706" stroke="#78350f" strokeWidth="1.5" />
          <circle cx="36" cy="78" r="3" fill="#ffffff" />
          <circle cx="37" cy="78" r="1.5" fill="#0f172a" />
          <circle cx="44" cy="78" r="3" fill="#ffffff" />
          <circle cx="45" cy="78" r="1.5" fill="#0f172a" />
          <path d="M 37 85 Q 40 88 44 85" stroke="#78350f" strokeWidth="1.5" fill="none" strokeLinecap="round" />
        </svg>
      </div>

      {/* 3. Chugging Vintage Cartoon Tractor */}
      <div className="cartoon-tractor-wrapper">
        <svg viewBox="0 0 120 70" className="tractor-svg">
          {/* Exhaust Pipe & Animated Smoke Puffs */}
          <rect x="34" y="14" width="4" height="14" fill="#64748b" />
          <g className="smoke-puffs">
            <circle cx="36" cy="8" r="4" fill="rgba(255,255,255,0.6)" className="smoke-1" />
            <circle cx="33" cy="2" r="6" fill="rgba(255,255,255,0.4)" className="smoke-2" />
          </g>

          {/* Tractor Engine Hood */}
          <path d="M 24 28 L 60 28 L 60 46 L 24 46 Z" fill="#ef4444" stroke="#991b1b" strokeWidth="2" />
          {/* Front Grille */}
          <rect x="22" y="30" width="3" height="14" rx="1" fill="#facc15" />
          {/* Cabin */}
          <path d="M 60 46 L 60 16 L 86 16 L 90 46 Z" fill="none" stroke="#ef4444" strokeWidth="3" />
          <path d="M 58 16 L 92 16" stroke="#dc2626" strokeWidth="4" strokeLinecap="round" />
          {/* Driver Seat & Little Sprout Driver */}
          <circle cx="75" cy="30" r="7" fill="#4ade80" />
          <circle cx="73" cy="28" r="1.2" fill="#0f172a" />
          <path d="M 75 23 Q 73 18 70 19" stroke="#16a34a" strokeWidth="1.5" fill="none" />

          {/* Steering Wheel */}
          <line x1="66" y1="36" x2="70" y2="44" stroke="#334155" strokeWidth="2.5" />
          <ellipse cx="65" cy="35" rx="2" ry="4" fill="#1e293b" />

          {/* Front Small Wheel */}
          <g className="tractor-wheel-front">
            <circle cx="34" cy="54" r="10" fill="#334155" stroke="#0f172a" strokeWidth="3" />
            <circle cx="34" cy="54" r="4" fill="#fbbf24" />
            <line x1="34" y1="46" x2="34" y2="62" stroke="#1e293b" strokeWidth="1.8" />
            <line x1="26" y1="54" x2="42" y2="54" stroke="#1e293b" strokeWidth="1.8" />
          </g>

          {/* Big Back Mud Wheel */}
          <g className="tractor-wheel-back">
            <circle cx="82" cy="50" r="16" fill="#334155" stroke="#0f172a" strokeWidth="3.5" />
            <circle cx="82" cy="50" r="7" fill="#fbbf24" stroke="#d97706" strokeWidth="1.5" />
            {/* Treads & Spokes */}
            <line x1="82" y1="36" x2="82" y2="64" stroke="#1e293b" strokeWidth="2.2" />
            <line x1="68" y1="50" x2="96" y2="50" stroke="#1e293b" strokeWidth="2.2" />
            <line x1="72" y1="40" x2="92" y2="60" stroke="#1e293b" strokeWidth="2" />
            <line x1="72" y1="60" x2="92" y2="40" stroke="#1e293b" strokeWidth="2" />
          </g>
        </svg>
      </div>

      {/* 4. Peekaboo Earthworm in corner */}
      <div className="peekaboo-worm">
        <svg viewBox="0 0 50 60" className="worm-svg">
          {/* Soil Mound */}
          <ellipse cx="25" cy="56" rx="22" ry="6" fill="#78350f" />
          {/* Pink Worm Body */}
          <path d="M 25 54 C 20 40, 32 30, 24 16" stroke="#f472b6" strokeWidth="8" strokeLinecap="round" fill="none" />
          {/* Cute Big Eyes */}
          <circle cx="21" cy="14" r="3" fill="#ffffff" />
          <circle cx="21" cy="14" r="1.5" fill="#0f172a" />
          <circle cx="27" cy="14" r="3" fill="#ffffff" />
          <circle cx="27" cy="14" r="1.5" fill="#0f172a" />
          {/* Tiny Glasses */}
          <rect x="17" y="11" width="7" height="6" rx="1.5" fill="none" stroke="#0284c7" strokeWidth="1" />
          <rect x="25" y="11" width="7" height="6" rx="1.5" fill="none" stroke="#0284c7" strokeWidth="1" />
          <line x1="24" y1="14" x2="25" y2="14" stroke="#0284c7" strokeWidth="1" />
          {/* Smile */}
          <path d="M 22 20 Q 25 23 27 20" stroke="#9d174d" strokeWidth="1.2" strokeLinecap="round" fill="none" />
        </svg>
      </div>
    </div>
  );
}
