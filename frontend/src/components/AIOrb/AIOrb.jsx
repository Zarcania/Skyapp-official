import React, { useState, useEffect } from 'react';
import './AIOrb.css';
import ChatInterface from './ChatInterface';

const AIOrb = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isVisible, setIsVisible] = useState(true);

  // Animation de pulsation pour attirer l'attention
  useEffect(() => {
    const pulseInterval = setInterval(() => {
      // L'animation CSS gère la pulsation
    }, 2000);

    return () => clearInterval(pulseInterval);
  }, []);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      {/* Orbe AI - Toujours visible en bas à droite */}
      <div className={`ai-orb-container ${isVisible ? 'visible' : ''}`}>
        <button
          className={`ai-orb ${isOpen ? 'active' : ''}`}
          onClick={toggleChat}
          aria-label="Assistant IA SkyApp"
          title="Assistant IA - Premier Logiciel BTP Intelligent"
        >
          {/* Cercle externe blanc */}
          <div className="orb-outer"></div>
          
          {/* Cercle interne noir */}
          <div className="orb-inner"></div>
          
          {/* Icône centrale */}
          <div className="orb-icon">
            {isOpen ? (
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            ) : (
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                <path d="M8 10h.01M12 10h.01M16 10h.01"></path>
              </svg>
            )}
          </div>

          {/* Point de notification (optionnel) */}
          <div className="orb-notification"></div>
        </button>

        {/* Badge "IA" */}
        <div className="ai-badge">
          <span>IA</span>
        </div>
      </div>

      {/* Interface de chat */}
      {isOpen && (
        <ChatInterface 
          isOpen={isOpen}
          onClose={() => setIsOpen(false)}
        />
      )}
    </>
  );
};

export default AIOrb;
