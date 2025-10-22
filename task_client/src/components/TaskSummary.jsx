const TaskSummary = ({ tasks }) => {
  const stats = {
    total: tasks.length,
    todo: tasks.filter(t => t.status === 'todo').length,
    in_progress: tasks.filter(t => t.status === 'in_progress').length,
    done: tasks.filter(t => t.status === 'done').length,
    blocked: tasks.filter(t => t.status === 'blocked').length,
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
      <div className="text-center p-3 bg-gray-50 rounded-lg">
        <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
        <p className="text-xs text-gray-600">Total</p>
      </div>
      <div className="text-center p-3 bg-blue-50 rounded-lg">
        <p className="text-2xl font-bold text-blue-600">{stats.todo}</p>
        <p className="text-xs text-blue-700">To Do</p>
      </div>
      <div className="text-center p-3 bg-yellow-50 rounded-lg">
        <p className="text-2xl font-bold text-yellow-600">{stats.in_progress}</p>
        <p className="text-xs text-yellow-700">In Progress</p>
      </div>
      <div className="text-center p-3 bg-green-50 rounded-lg">
        <p className="text-2xl font-bold text-green-600">{stats.done}</p>
        <p className="text-xs text-green-700">Done</p>
      </div>
      <div className="text-center p-3 bg-red-50 rounded-lg">
        <p className="text-2xl font-bold text-red-600">{stats.blocked}</p>
        <p className="text-xs text-red-700">Blocked</p>
      </div>
    </div>
  );
};

export default TaskSummary;
