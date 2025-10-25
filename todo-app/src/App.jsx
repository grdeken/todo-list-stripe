import { useState, useEffect } from 'react';
import Login from './components/Login';
import TodoList from './components/TodoList';
import Navigation from './components/Navigation';
import UpgradeModal from './components/UpgradeModal';
import Settings from './components/Settings';
import PremiumWelcomeModal from './components/PremiumWelcomeModal';
import { api } from './api';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [todoList, setTodoList] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showPremiumWelcome, setShowPremiumWelcome] = useState(false);

  useEffect(() => {
    // Check for OAuth callback token in URL
    const urlParams = new URLSearchParams(window.location.search);
    const oauthToken = urlParams.get('token');

    if (oauthToken) {
      // Store the OAuth token
      localStorage.setItem('access_token', oauthToken);

      // Fetch user info with the new token
      const fetchOAuthUser = async () => {
        try {
          // For now, we'll decode the user info from the token or fetch it
          // Since we don't have a /me endpoint yet, we'll create a minimal user object
          const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}/auth/me`, {
            headers: {
              'Authorization': `Bearer ${oauthToken}`,
              'Content-Type': 'application/json',
            },
          });

          if (response.ok) {
            const userData = await response.json();
            localStorage.setItem('user', JSON.stringify(userData));
            setUser(userData);
            await loadTodoList();
            await loadSubscription();

            // Clean up the URL
            window.history.replaceState({}, document.title, window.location.pathname);
          } else {
            setLoading(false);
          }
        } catch (error) {
          console.error('Error fetching OAuth user:', error);
          setLoading(false);
        }
      };

      fetchOAuthUser();
      return;
    }

    // Check if user is already logged in
    const token = localStorage.getItem('access_token');
    const savedUser = localStorage.getItem('user');
    if (token && savedUser) {
      setUser(JSON.parse(savedUser));
      loadTodoList();
      loadSubscription();

      // Check for Stripe checkout success
      handleStripeRedirect();
    } else {
      setLoading(false);
    }
  }, []);

  const loadTodoList = async () => {
    try {
      const lists = await api.getTodoLists();
      if (Array.isArray(lists) && lists.length > 0) {
        // Ensure todos is always an array
        const list = lists[0];
        setTodoList({ ...list, todos: list.todos || [] });
      } else {
        // Create a default todo list if none exists
        const newList = await api.createTodoList('My Todo List');
        // Ensure todos is always an array
        setTodoList({ ...newList, todos: newList.todos || [] });
      }
    } catch (error) {
      console.error('Error loading todo list:', error);
      // Clear user and show login again on auth error
      if (error.message?.includes('401') || error.message?.includes('403')) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        setUser(null);
      }
    } finally {
      setLoading(false);
    }
  };

  const loadSubscription = async () => {
    try {
      const subStatus = await api.getSubscriptionStatus();
      setSubscription(subStatus);
    } catch (error) {
      console.error('Error loading subscription:', error);
    }
  };

  const handleLogin = async (userData) => {
    setUser(userData);
    setLoading(true);
    await loadTodoList();
    await loadSubscription();
  };

  const handleLogout = async () => {
    await api.logout();
    setUser(null);
    setTodoList(null);
    setSubscription(null);
  };

  const handleUpdateTodoList = (updatedList) => {
    // Ensure todos is always an array
    setTodoList({ ...updatedList, todos: updatedList.todos || [] });
  };

  const handleUpgrade = async () => {
    try {
      const { session_url } = await api.createCheckoutSession();
      // Redirect to Stripe checkout
      window.location.href = session_url;
    } catch (error) {
      console.error('Error creating checkout session:', error);
      alert('Failed to start checkout. Please try again.');
    }
  };

  const handleShowUpgradeModal = () => {
    setShowUpgradeModal(true);
  };

  const handleCloseUpgradeModal = () => {
    setShowUpgradeModal(false);
  };

  const handleTodoLimitReached = () => {
    setShowUpgradeModal(true);
  };

  const handleShowSettings = () => {
    setShowSettings(true);
  };

  const handleCloseSettings = () => {
    setShowSettings(false);
  };

  const handleStripeRedirect = async () => {
    // Check for session_id in URL (from Stripe redirect)
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');

    if (sessionId) {
      try {
        // Verify the session with backend
        await api.verifyCheckoutSession(sessionId);

        // Reload subscription status
        await loadSubscription();

        // Show premium welcome modal
        setShowPremiumWelcome(true);

        // Clean up URL
        window.history.replaceState({}, document.title, window.location.pathname);
      } catch (error) {
        console.error('Error verifying checkout session:', error);
      }
    }
  };

  const handleClosePremiumWelcome = () => {
    setShowPremiumWelcome(false);
  };

  if (loading) {
    return (
      <div className="app">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="app">
      {!user ? (
        <Login onLogin={handleLogin} />
      ) : showSettings ? (
        <Settings
          user={user}
          subscription={subscription}
          onBack={handleCloseSettings}
          onUpdateUser={setUser}
        />
      ) : (
        <>
          <Navigation
            user={user}
            subscription={subscription}
            onLogout={handleLogout}
            onUpgrade={handleShowUpgradeModal}
            onShowSettings={handleShowSettings}
          />
          <TodoList
            todoList={todoList}
            subscription={subscription}
            onUpdateTodoList={handleUpdateTodoList}
            onTodoLimitReached={handleTodoLimitReached}
            onSubscriptionUpdate={loadSubscription}
          />
          <UpgradeModal
            isOpen={showUpgradeModal}
            onClose={handleCloseUpgradeModal}
            onUpgrade={handleUpgrade}
            subscription={subscription}
          />
          <PremiumWelcomeModal
            isOpen={showPremiumWelcome}
            onClose={handleClosePremiumWelcome}
          />
        </>
      )}
    </div>
  );
}

export default App;
