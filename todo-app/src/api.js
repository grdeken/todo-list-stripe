const API_BASE_URL = 'http://localhost:8000/api/v1';

const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  };
};

export const api = {
  // Authentication
  async register(email, password, username) {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, username }),
    });
    const data = await response.json();
    if (response.ok) {
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
    }
    return { ok: response.ok, data };
  },

  async login(email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login-json`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    if (response.ok) {
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
    }
    return { ok: response.ok, data };
  },

  async logout() {
    const response = await fetch(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    return { ok: response.ok };
  },

  async changePassword(currentPassword, newPassword) {
    const response = await fetch(`${API_BASE_URL}/auth/change-password`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to change password');
    }
    return data;
  },

  // TodoLists
  async getTodoLists() {
    const response = await fetch(`${API_BASE_URL}/todo-lists/`, {
      headers: getAuthHeaders(),
    });
    return response.json();
  },

  async createTodoList(name) {
    const response = await fetch(`${API_BASE_URL}/todo-lists/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ name }),
    });
    return response.json();
  },

  async getTodoList(id) {
    const response = await fetch(`${API_BASE_URL}/todo-lists/${id}`, {
      headers: getAuthHeaders(),
    });
    return response.json();
  },

  async updateTodoList(id, name) {
    const response = await fetch(`${API_BASE_URL}/todo-lists/${id}`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify({ name }),
    });
    return response.json();
  },

  async deleteTodoList(id) {
    const response = await fetch(`${API_BASE_URL}/todo-lists/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    return { ok: response.ok };
  },

  // Todos
  async createTodo(todoListId, description, dueDate = null) {
    const response = await fetch(`${API_BASE_URL}/todos/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        todo_list_id: todoListId,
        description,
        due_date: dueDate,
      }),
    });
    return response.json();
  },

  async updateTodo(id, data) {
    const response = await fetch(`${API_BASE_URL}/todos/${id}`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return response.json();
  },

  async toggleTodo(id) {
    const response = await fetch(`${API_BASE_URL}/todos/${id}/toggle`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    return response.json();
  },

  async deleteTodo(id) {
    const response = await fetch(`${API_BASE_URL}/todos/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    return { ok: response.ok };
  },

  // Subscription
  async getSubscriptionStatus() {
    const response = await fetch(`${API_BASE_URL}/subscription/status`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to fetch subscription status');
    }
    return response.json();
  },

  async createCheckoutSession(successUrl = null, cancelUrl = null) {
    const response = await fetch(`${API_BASE_URL}/subscription/checkout`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        success_url: successUrl,
        cancel_url: cancelUrl,
      }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to create checkout session');
    }
    return data;
  },

  async cancelSubscription() {
    const response = await fetch(`${API_BASE_URL}/subscription/cancel`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to cancel subscription');
    }
    return data;
  },

  async getCustomerPortal() {
    const response = await fetch(`${API_BASE_URL}/subscription/portal`, {
      headers: getAuthHeaders(),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to get customer portal');
    }
    return data;
  },

  async verifyCheckoutSession(sessionId) {
    const response = await fetch(`${API_BASE_URL}/subscription/verify-session/${sessionId}`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to verify checkout session');
    }
    return data;
  },
};
