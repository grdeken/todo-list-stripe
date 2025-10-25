const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const getAuthHeaders = () => {
  // Authentication now uses HttpOnly cookies instead of localStorage
  // for better security (XSS protection)
  return {
    'Content-Type': 'application/json',
  };
};

// Helper to include credentials for cookie-based auth
const getFetchOptions = (options = {}) => {
  return {
    ...options,
    credentials: 'include', // Send cookies with requests
  };
};

export const api = {
  // Authentication
  async register(email, password, username) {
    const response = await fetch(`${API_BASE_URL}/auth/register`, getFetchOptions({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, username }),
    }));
    const data = await response.json();
    // Token is now in HttpOnly cookie - no need to store in localStorage
    // Just store user data for display purposes
    if (response.ok) {
      localStorage.setItem('user', JSON.stringify(data));
    }
    return { ok: response.ok, data };
  },

  async login(email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login-json`, getFetchOptions({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    }));
    const data = await response.json();
    // Token is now in HttpOnly cookie - no need to store in localStorage
    // Just store user data for display purposes
    if (response.ok) {
      localStorage.setItem('user', JSON.stringify(data));
    }
    return { ok: response.ok, data };
  },

  async logout() {
    const response = await fetch(`${API_BASE_URL}/auth/logout`, getFetchOptions({
      method: 'POST',
      headers: getAuthHeaders(),
    }));
    // Clear user data (cookie is cleared by backend)
    localStorage.removeItem('user');
    return { ok: response.ok };
  },

  async changePassword(currentPassword, newPassword) {
    const response = await fetch(`${API_BASE_URL}/auth/change-password`, getFetchOptions({
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    }));
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to change password');
    }
    return data;
  },

  // TodoLists
  async getTodoLists() {
    const response = await fetch(`${API_BASE_URL}/todo-lists/`, getFetchOptions({
      headers: getAuthHeaders(),
    }));
    return response.json();
  },

  async createTodoList(name) {
    const response = await fetch(`${API_BASE_URL}/todo-lists/`, getFetchOptions({
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ name }),
    }));
    return response.json();
  },

  async getTodoList(id) {
    const response = await fetch(`${API_BASE_URL}/todo-lists/${id}`, getFetchOptions({
      headers: getAuthHeaders(),
    }));
    return response.json();
  },

  async updateTodoList(id, name) {
    const response = await fetch(`${API_BASE_URL}/todo-lists/${id}`, getFetchOptions({
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify({ name }),
    }));
    return response.json();
  },

  async deleteTodoList(id) {
    const response = await fetch(`${API_BASE_URL}/todo-lists/${id}`, getFetchOptions({
      method: 'DELETE',
      headers: getAuthHeaders(),
    }));
    return { ok: response.ok };
  },

  // Todos
  async createTodo(todoListId, description, dueDate = null) {
    const response = await fetch(`${API_BASE_URL}/todos/`, getFetchOptions({
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        todo_list_id: todoListId,
        description,
        due_date: dueDate,
      }),
    }));
    return response.json();
  },

  async updateTodo(id, data) {
    const response = await fetch(`${API_BASE_URL}/todos/${id}`, getFetchOptions({
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    }));
    return response.json();
  },

  async toggleTodo(id) {
    const response = await fetch(`${API_BASE_URL}/todos/${id}/toggle`, getFetchOptions({
      method: 'POST',
      headers: getAuthHeaders(),
    }));
    return response.json();
  },

  async deleteTodo(id) {
    const response = await fetch(`${API_BASE_URL}/todos/${id}`, getFetchOptions({
      method: 'DELETE',
      headers: getAuthHeaders(),
    }));
    return { ok: response.ok };
  },

  // Subscription
  async getSubscriptionStatus() {
    const response = await fetch(`${API_BASE_URL}/subscription/status`, getFetchOptions({
      headers: getAuthHeaders(),
    }));
    if (!response.ok) {
      throw new Error('Failed to fetch subscription status');
    }
    return response.json();
  },

  async createCheckoutSession(successUrl = null, cancelUrl = null) {
    const response = await fetch(`${API_BASE_URL}/subscription/checkout`, getFetchOptions({
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        success_url: successUrl,
        cancel_url: cancelUrl,
      }),
    }));
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to create checkout session');
    }
    return data;
  },

  async cancelSubscription() {
    const response = await fetch(`${API_BASE_URL}/subscription/cancel`, getFetchOptions({
      method: 'POST',
      headers: getAuthHeaders(),
    }));
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to cancel subscription');
    }
    return data;
  },

  async getCustomerPortal() {
    const response = await fetch(`${API_BASE_URL}/subscription/portal`, getFetchOptions({
      headers: getAuthHeaders(),
    }));
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to get customer portal');
    }
    return data;
  },

  async verifyCheckoutSession(sessionId) {
    const response = await fetch(`${API_BASE_URL}/subscription/verify-session/${sessionId}`, getFetchOptions({
      method: 'POST',
      headers: getAuthHeaders(),
    }));
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to verify checkout session');
    }
    return data;
  },
};
