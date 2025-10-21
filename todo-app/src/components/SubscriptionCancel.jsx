function SubscriptionCancel({ onContinue }) {
  return (
    <div className="subscription-result">
      <div className="result-card cancel">
        <div className="result-icon">ℹ</div>
        <h1>Checkout Cancelled</h1>
        <p>You cancelled the checkout process.</p>
        <p className="result-message">
          No charges were made. You can upgrade anytime from the app.
        </p>
        <button className="btn-primary" onClick={onContinue}>
          Return to App
        </button>
      </div>
    </div>
  );
}

export default SubscriptionCancel;
