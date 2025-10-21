import { useState } from 'react';
import TodoItem from './TodoItem';
import { api } from '../api';

const TodoList = ({ todoList, subscription, onUpdateTodoList, onTodoLimitReached, onSubscriptionUpdate }) => {
  const [description, setDescription] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [isEditingName, setIsEditingName] = useState(false);
  const [listName, setListName] = useState(todoList?.name || '');
  const [savingName, setSavingName] = useState(false);
  const [error, setError] = useState('');

  // Return loading state if todoList is null or todos is undefined
  if (!todoList || !todoList.todos) {
    return (
      <div className="todo-list-container">
        <div className="header">
          <h1>Loading...</h1>
          <button onClick={onLogout} className="btn-logout">
            Logout
          </button>
        </div>
      </div>
    );
  }

  const handleAddTodo = async (e) => {
    e.preventDefault();
    if (description.trim()) {
      // Check if user can create todos before attempting
      if (subscription && !subscription.can_create_todos) {
        onTodoLimitReached();
        return;
      }

      setLoading(true);
      setError('');
      try {
        const newTodo = await api.createTodo(
          todoList.id,
          description,
          dueDate || null
        );
        onUpdateTodoList({
          ...todoList,
          todos: [...todoList.todos, newTodo],
        });
        setDescription('');
        setDueDate('');
        // Refresh subscription to update todo count
        if (onSubscriptionUpdate) {
          await onSubscriptionUpdate();
        }
      } catch (error) {
        console.error('Error adding todo:', error);
        // Check if error is due to limit reached
        const errorText = await error.text?.() || error.message || '';
        if (errorText.includes('limit') || errorText.includes('403')) {
          setError('You have reached your todo limit. Upgrade to premium for unlimited todos!');
          onTodoLimitReached();
        } else {
          setError('Failed to add todo. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    }
  };

  const handleToggleTodo = async (todoId) => {
    try {
      const toggleResponse = await api.toggleTodo(todoId);
      // FastAPI returns {id, complete, message}, update the todo locally
      onUpdateTodoList({
        ...todoList,
        todos: todoList.todos.map((todo) =>
          todo.id === todoId ? { ...todo, complete: toggleResponse.complete } : todo
        ),
      });
    } catch (error) {
      console.error('Error toggling todo:', error);
    }
  };

  const handleDeleteTodo = async (todoId) => {
    try {
      await api.deleteTodo(todoId);
      onUpdateTodoList({
        ...todoList,
        todos: todoList.todos.filter((todo) => todo.id !== todoId),
      });
      // Refresh subscription to update todo count
      if (onSubscriptionUpdate) {
        await onSubscriptionUpdate();
      }
    } catch (error) {
      console.error('Error deleting todo:', error);
    }
  };

  const handleSaveListName = async () => {
    if (listName.trim() && listName !== todoList.name) {
      setSavingName(true);
      try {
        const updatedList = await api.updateTodoList(todoList.id, listName.trim());
        onUpdateTodoList(updatedList);
        setIsEditingName(false);
      } catch (error) {
        console.error('Error updating list name:', error);
        setListName(todoList.name); // Revert on error
      } finally {
        setSavingName(false);
      }
    } else {
      setIsEditingName(false);
      setListName(todoList.name); // Revert if empty or unchanged
    }
  };

  const handleCancelEdit = () => {
    setListName(todoList.name);
    setIsEditingName(false);
  };

  const canAddTodos = !subscription || subscription.can_create_todos;

  return (
    <div className="todo-list-container">
        <div className="header">
          {isEditingName ? (
            <div className="edit-list-name">
              <input
                type="text"
                value={listName}
                onChange={(e) => setListName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSaveListName();
                  if (e.key === 'Escape') handleCancelEdit();
                }}
                className="list-name-input"
                autoFocus
                disabled={savingName}
              />
              <button
                onClick={handleSaveListName}
                className="btn-save btn-edit"
                disabled={savingName}
              >
                {savingName ? '...' : '✓'}
              </button>
              <button
                onClick={handleCancelEdit}
                className="btn-cancel btn-edit"
                disabled={savingName}
              >
                ✕
              </button>
            </div>
          ) : (
            <h1 onClick={() => setIsEditingName(true)} className="editable-title">
              {todoList.name}
            </h1>
          )}
        </div>

      <form onSubmit={handleAddTodo} className="add-todo-form">
        {error && <div className="error-message">{error}</div>}
        <div className="form-row">
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Add a new todo..."
            className="todo-input"
            disabled={!canAddTodos}
          />
          <input
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            className="date-input"
            disabled={!canAddTodos}
          />
          <button
            type="submit"
            className="btn-add"
            disabled={loading || !canAddTodos}
            title={!canAddTodos ? 'Upgrade to add more todos' : ''}
          >
            {loading ? 'Adding...' : 'Add'}
          </button>
        </div>
        {!canAddTodos && (
          <div className="limit-warning">
            You've reached your free limit. Upgrade to premium for unlimited todos!
          </div>
        )}
      </form>

      <div className="todos-container">
        {todoList.todos.length === 0 ? (
          <p className="empty-message">No todos yet. Add one to get started!</p>
        ) : (
          todoList.todos.map((todo) => (
            <TodoItem
              key={todo.id}
              todo={todo}
              onToggle={handleToggleTodo}
              onDelete={handleDeleteTodo}
            />
          ))
        )}
      </div>

      <div className="stats">
        <span>
          Total: {todoList.todos.length} | Completed:{' '}
          {todoList.todos.filter((t) => t.complete).length}
        </span>
      </div>
    </div>
  );
};

export default TodoList;
