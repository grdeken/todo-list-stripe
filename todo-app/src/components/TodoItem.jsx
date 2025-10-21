const TodoItem = ({ todo, onToggle, onDelete }) => {
  const formatDate = (date) => {
    if (!date) return '';
    return new Date(date).toLocaleDateString();
  };

  return (
    <div className={`todo-item ${todo.complete ? 'completed' : ''}`}>
      <input
        type="checkbox"
        checked={todo.complete}
        onChange={() => onToggle(todo.id)}
        className="todo-checkbox"
      />
      <div className="todo-content">
        <span className="todo-description">{todo.description}</span>
        {(todo.dueDate || todo.due_date) && (
          <span className="todo-due-date">Due: {formatDate(todo.dueDate || todo.due_date)}</span>
        )}
      </div>
      <button onClick={() => onDelete(todo.id)} className="btn-delete">
        Delete
      </button>
    </div>
  );
};

export default TodoItem;
