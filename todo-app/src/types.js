/**
 * Data models for the Todo List Manager
 */

/**
 * User object
 * @typedef {Object} User
 * @property {string} email - User's email address
 * @property {string} password - User's password
 */

/**
 * Todo item object
 * @typedef {Object} Todo
 * @property {string} id - Unique identifier
 * @property {string} description - Description of the todo
 * @property {boolean} complete - Whether the todo is completed
 * @property {Date|string} dueDate - Due date for the todo
 */

/**
 * TodoList object
 * @typedef {Object} TodoList
 * @property {string} id - Unique identifier
 * @property {string} name - Name of the todo list
 * @property {Todo[]} todos - Array of todo items
 */

export const createUser = (email, password) => ({
  email,
  password,
});

export const createTodo = (description, dueDate = null) => ({
  id: crypto.randomUUID(),
  description,
  complete: false,
  dueDate,
});

export const createTodoList = (name) => ({
  id: crypto.randomUUID(),
  name,
  todos: [],
});
