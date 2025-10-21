import { useState } from 'react';
import { api } from '../api';

function Settings({ user, subscription, onBack, onUpdateUser }) {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState('');
  const [isChangingPassword, setIsChangingPassword] = useState(false);

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setPasswordError('');
    setPasswordSuccess('');

    if (newPassword !== confirmPassword) {
      setPasswordError('New passwords do not match');
      return;
    }

    if (newPassword.length < 8) {
      setPasswordError('Password must be at least 8 characters');
      return;
    }

    setIsChangingPassword(true);
    try {
      await api.changePassword(currentPassword, newPassword);
      setPasswordSuccess('Password changed successfully');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (error) {
      setPasswordError(error.message || 'Failed to change password');
    } finally {
      setIsChangingPassword(false);
    }
  };

  const handleManageSubscription = async () => {
    try {
      const { portal_url } = await api.getCustomerPortal();
      window.location.href = portal_url;
    } catch (error) {
      console.error('Error getting customer portal:', error);
      alert('Failed to open subscription management. Please try again.');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatAmount = (amount) => {
    if (!amount) return '$0.00';
    return `$${(amount / 100).toFixed(2)}`;
  };

  return (
    <div className="settings-container">
      <div className="settings-header">
        <button onClick={onBack} className="btn-back">
          ← Back to Todos
        </button>
        <h1>Settings</h1>
      </div>

      {/* Profile Section */}
      <section className="settings-section">
        <h2 className="section-title">Profile</h2>
        <div className="settings-card">
          <div className="settings-row">
            <span className="settings-label">Email</span>
            <span className="settings-value">{user?.email}</span>
          </div>
          <div className="settings-row">
            <span className="settings-label">Username</span>
            <span className="settings-value">{user?.username}</span>
          </div>
        </div>
      </section>

      {/* Password Section */}
      <section className="settings-section">
        <h2 className="section-title">Change Password</h2>
        <div className="settings-card">
          {passwordSuccess && (
            <div className="success-message">{passwordSuccess}</div>
          )}
          {passwordError && (
            <div className="error-message">{passwordError}</div>
          )}
          <form onSubmit={handlePasswordChange}>
            <div className="form-group">
              <label htmlFor="current-password">Current Password</label>
              <input
                type="password"
                id="current-password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="new-password">New Password</label>
              <input
                type="password"
                id="new-password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                minLength={8}
              />
            </div>
            <div className="form-group">
              <label htmlFor="confirm-password">Confirm New Password</label>
              <input
                type="password"
                id="confirm-password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={8}
              />
            </div>
            <button
              type="submit"
              className="btn-primary"
              disabled={isChangingPassword}
            >
              {isChangingPassword ? 'Changing Password...' : 'Change Password'}
            </button>
          </form>
        </div>
      </section>

      {/* Subscription Section */}
      <section className="settings-section">
        <h2 className="section-title">Subscription</h2>
        <div className="settings-card">
          <div className="settings-row">
            <span className="settings-label">Plan</span>
            <span className="settings-value">
              {subscription?.subscription_tier === 'premium' ? 'Premium' : 'Free'}
            </span>
          </div>
          {subscription?.subscription_tier === 'premium' && (
            <>
              <div className="settings-row">
                <span className="settings-label">Monthly Amount</span>
                <span className="settings-value">
                  {formatAmount(subscription?.monthly_amount)}
                </span>
              </div>
              <div className="settings-row">
                <span className="settings-label">Next Billing Date</span>
                <span className="settings-value">
                  {formatDate(subscription?.next_billing_date)}
                </span>
              </div>
              <div className="settings-row">
                <span className="settings-label">Status</span>
                <span className="settings-value">
                  {subscription?.subscription_status === 'active' ? 'Active' : subscription?.subscription_status}
                </span>
              </div>
            </>
          )}
          <div className="settings-actions">
            <button
              onClick={handleManageSubscription}
              className="btn-secondary"
            >
              Manage Subscription
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Settings;
