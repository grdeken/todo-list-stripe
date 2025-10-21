import React from 'react';

function PremiumWelcomeModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal premium-welcome-modal" onClick={(e) => e.stopPropagation()}>
        <div className="premium-welcome-content">
          <div className="premium-celebration-icon">🎉</div>
          <h2 className="premium-welcome-header">Woohoo, you just went premium!</h2>
          <p className="premium-welcome-body">
            You now have access to all features and unlimited usage
          </p>
          <button className="btn-premium-continue" onClick={onClose}>
            Go to my lists
          </button>
        </div>
      </div>
    </div>
  );
}

export default PremiumWelcomeModal;
