import { useState } from 'react';
import { api } from '../api';

function SubscriptionSettings({ subscription, onSubscriptionUpdate }) {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  if (!subscription) {
    return <div>Loading subscription info...</div>;
  }

  const isPremium = subscription.subscription_tier === 'premium';

  const handleManageBilling = async () => {
    setLoading(true);
    try {
      const { portal_url } = await api.getCustomerPortal();
      window.location.href = portal_url;
    } catch (error) {
      console.error('Error opening customer portal:', error);
      setMessage('Failed to open billing portal. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelSubscription = async () => {
    if (!confirm('Are you sure you want to cancel your subscription? You will lose access to premium features at the end of your billing period.')) {
      return;
    }

    setLoading(true);
    setMessage('');
    try {
      await api.cancelSubscription();
      setMessage('Subscription will be canceled at the end of your billing period.');
      if (onSubscriptionUpdate) {
        await onSubscriptionUpdate();
      }
    } catch (error) {
      console.error('Error canceling subscription:', error);
      setMessage('Failed to cancel subscription. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="subscription-settings">
      <h2>Subscription Settings</h2>

      {message && <div className="settings-message">{message}</div>}

      <div className="settings-card">
        <div className="settings-row">
          <span className="settings-label">Current Plan:</span>
          <span className="settings-value">
            {isPremium ? 'Premium' : 'Free'}
            {isPremium && subscription.subscription_status === 'canceled' && (
              <span className="status-badge canceled"> (Canceling)</span>
            )}
          </span>
        </div>

        <div className="settings-row">
          <span className="settings-label">Status:</span>
          <span className="settings-value">
            {subscription.subscription_status}
          </span>
        </div>

        <div className="settings-row">
          <span className="settings-label">Todos:</span>
          <span className="settings-value">
            {subscription.todo_count}
            {subscription.todo_limit ? ` / ${subscription.todo_limit}` : ' (Unlimited)'}
          </span>
        </div>

        {isPremium && subscription.subscription_start_date && (
          <div className="settings-row">
            <span className="settings-label">Member Since:</span>
            <span className="settings-value">
              {new Date(subscription.subscription_start_date).toLocaleDateString()}
            </span>
          </div>
        )}
      </div>

      {isPremium && (
        <div className="settings-actions">
          <button
            className="btn-secondary"
            onClick={handleManageBilling}
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Manage Billing'}
          </button>

          {subscription.subscription_status === 'active' && (
            <button
              className="btn-danger"
              onClick={handleCancelSubscription}
              disabled={loading}
            >
              {loading ? 'Processing...' : 'Cancel Subscription'}
            </button>
          )}
        </div>
      )}
    </div>
  );
}

export default SubscriptionSettings;
