function SubscriptionBadge({ subscription, onUpgrade }) {
  if (!subscription) return null;

  const { subscription_tier, todo_count, todo_limit } = subscription;
  const isPremium = subscription_tier === 'premium';

  return (
    <div
      className={`subscription-badge ${isPremium ? 'premium' : 'free'}`}
      onClick={!isPremium ? onUpgrade : undefined}
      style={{ cursor: !isPremium ? 'pointer' : 'default' }}
    >
      {isPremium ? (
        <span className="badge-content">
          <span className="badge-icon">⭐</span>
          <span className="badge-text">Premium</span>
        </span>
      ) : (
        <span className="badge-content">
          <span className="badge-text">
            Free ({todo_count}/{todo_limit} todos)
          </span>
        </span>
      )}
    </div>
  );
}

export default SubscriptionBadge;
