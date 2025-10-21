import { useState } from 'react';
import SubscriptionBadge from './SubscriptionBadge';
import UpgradeButton from './UpgradeButton';

function Navigation({ user, subscription, onLogout, onUpgrade }) {
  const showUpgradeButton = subscription?.subscription_tier === 'free' &&
                           subscription?.todo_count >= subscription?.todo_limit;

  return (
    <nav className="navigation">
      <div className="nav-container">
        <div className="nav-left">
          <h1 className="nav-logo">Todo List</h1>
          {subscription && (
            <SubscriptionBadge subscription={subscription} onUpgrade={onUpgrade} />
          )}
        </div>

        <div className="nav-center">
        </div>

        <div className="nav-right">
          {showUpgradeButton && (
            <UpgradeButton onUpgrade={onUpgrade} />
          )}

          <div className="user-info">
            <span className="username">{user?.username || user?.email}</span>
            <button onClick={onLogout} className="btn-logout">
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navigation;
