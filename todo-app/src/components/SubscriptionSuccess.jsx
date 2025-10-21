import { useEffect, useState } from 'react';
import PremiumWelcomeModal from './PremiumWelcomeModal';

function SubscriptionSuccess({ onContinue }) {
  const [showModal, setShowModal] = useState(true);

  useEffect(() => {
    // Don't auto-redirect, let user click the button
  }, []);

  const handleContinue = () => {
    setShowModal(false);
    if (onContinue) onContinue();
  };

  return (
    <>
      <PremiumWelcomeModal
        isOpen={showModal}
        onClose={handleContinue}
      />
      {!showModal && (
        <div className="subscription-result">
          <div className="result-card success">
            <div className="result-icon">✓</div>
            <h1>Welcome to Premium!</h1>
            <p>Your subscription has been activated successfully.</p>
            <p className="result-message">
              You now have unlimited access to create todos.
            </p>
            <button className="btn-primary" onClick={onContinue}>
              Continue to App
            </button>
          </div>
        </div>
      )}
    </>
  );
}

export default SubscriptionSuccess;
