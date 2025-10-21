import { useEffect } from 'react';

function SubscriptionSuccess({ onContinue }) {
  useEffect(() => {
    // Auto-redirect after 5 seconds
    const timer = setTimeout(() => {
      if (onContinue) onContinue();
    }, 5000);

    return () => clearTimeout(timer);
  }, [onContinue]);

  return (
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
  );
}

export default SubscriptionSuccess;
