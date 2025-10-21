import { useState, useEffect } from 'react';
import Login from './components/Login';
import TodoList from './components/TodoList';
import Navigation from './components/Navigation';
import UpgradeModal from './components/UpgradeModal';
import { api } from './api';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [todoList, setTodoList] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('access_token');
    const savedUser = localStorage.getItem('user');
    if (token && savedUser) {
      setUser(JSON.parse(savedUser));
      loadTodoList();
      loadSubscription();
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
      ) : (
        <>
          <Navigation
            user={user}
            subscription={subscription}
            onLogout={handleLogout}
            onUpgrade={handleShowUpgradeModal}
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
        </>
      )}
    </div>
  );
}

export default App;
