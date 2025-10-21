function UpgradeModal({ isOpen, onClose, onUpgrade, subscription }) {
  if (!isOpen) return null;

  const { todo_count, todo_limit } = subscription || {};

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Upgrade to Premium</h2>
          <button className="modal-close" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="modal-body">
          <div className="upgrade-message">
            <p className="limit-message">
              You've reached your limit of {todo_limit} todos!
            </p>
            <p className="current-count">
              Current todos: <strong>{todo_count}/{todo_limit}</strong>
            </p>
          </div>

          <div className="premium-benefits">
            <h3>Premium Benefits</h3>
            <ul>
              <li>✓ Unlimited todos</li>
              <li>✓ Create as many lists as you want</li>
              <li>✓ Priority support</li>
              <li>✓ Future premium features</li>
            </ul>
          </div>

          <div className="pricing">
            <div className="price-tag">
              <span className="price">$9.99</span>
              <span className="period">/month</span>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-cancel" onClick={onClose}>
            Maybe Later
          </button>
          <button className="btn-upgrade-primary" onClick={onUpgrade}>
            Upgrade Now
          </button>
        </div>
      </div>
    </div>
  );
}

export default UpgradeModal;
