function UpgradeButton({ onUpgrade, disabled = false }) {
  return (
    <button
      className="btn-upgrade"
      onClick={onUpgrade}
      disabled={disabled}
      title="Upgrade to Premium for unlimited todos"
    >
      Upgrade to Premium
    </button>
  );
}

export default UpgradeButton;
