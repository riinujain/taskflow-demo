import { useState } from 'react';
import { tasksAPI } from '../services/api';

const TaskList = ({ tasks, onTaskUpdated, onTaskDeleted }) => {
  const [updatingId, setUpdatingId] = useState(null);

  const getPriorityColor = (priority) => {
    const colors = {
      low: 'bg-gray-100 text-gray-800',
      medium: 'bg-blue-100 text-blue-800',
      high: 'bg-orange-100 text-orange-800',
      critical: 'bg-red-100 text-red-800',
    };
    return colors[priority] || colors.medium;
  };

  const getStatusColor = (status) => {
    const colors = {
      todo: 'text-blue-600',
      in_progress: 'text-yellow-600',
      done: 'text-green-600',
      blocked: 'text-red-600',
    };
    return colors[status] || colors.todo;
  };

  const handleStatusChange = async (task, newStatus) => {
    try {
      setUpdatingId(task.id);
      const updatedTask = await tasksAPI.update(task.id, { status: newStatus });
      onTaskUpdated(updatedTask);
    } catch (error) {
      console.error('Failed to update task:', error);
    } finally {
      setUpdatingId(null);
    }
  };

  const handleDelete = async (taskId) => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      await tasksAPI.delete(taskId);
      onTaskDeleted(taskId);
    } catch (error) {
      console.error('Failed to delete task:', error);
    }
  };

  if (tasks.length === 0) {
    return (
      <div className="card text-center py-12">
        <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No tasks yet</h3>
        <p className="text-gray-500">Create your first task to get started</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {tasks.map((task) => (
        <div key={task.id} className="card">
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-2">
                <h3 className="text-lg font-semibold text-gray-900">{task.title}</h3>
                <span className={`badge ${getPriorityColor(task.priority)}`}>
                  {task.priority}
                </span>
              </div>
              <p className="text-gray-600 text-sm">{task.description || 'No description'}</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-gray-100">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-500">Status:</span>
                <select
                  value={task.status}
                  onChange={(e) => handleStatusChange(task, e.target.value)}
                  disabled={updatingId === task.id}
                  className={`text-sm font-medium px-3 py-1 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none ${getStatusColor(task.status)} disabled:opacity-50`}
                >
                  <option value="todo">To Do</option>
                  <option value="in_progress">In Progress</option>
                  <option value="done">Done</option>
                  <option value="blocked">Blocked</option>
                </select>
              </div>

              {task.due_date && (
                <div className="flex items-center space-x-1 text-sm text-gray-500">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span>{new Date(task.due_date).toLocaleDateString()}</span>
                </div>
              )}
            </div>

            <button
              onClick={() => handleDelete(task.id)}
              className="text-red-600 hover:text-red-800 text-sm font-medium transition-colors"
            >
              Delete
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default TaskList;
