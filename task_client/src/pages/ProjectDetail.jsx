import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectsAPI, tasksAPI } from '../services/api';
import TaskSummary from '../components/TaskSummary';
import TaskList from '../components/TaskList';
import CreateTaskModal from '../components/CreateTaskModal';

const ProjectDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [filter, setFilter] = useState('all');

  const loadProjectAndTasks = async () => {
    try {
      setLoading(true);
      const [projectData, tasksData] = await Promise.all([
        projectsAPI.getById(id),
        tasksAPI.getByProject(id),
      ]);
      setProject(projectData);
      setTasks(tasksData);
    } catch (error) {
      console.error('Failed to load project:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProjectAndTasks();
  }, [id]);

  const handleTaskCreated = (newTask) => {
    setTasks([newTask, ...tasks]);
    setShowCreateModal(false);
  };

  const handleTaskUpdated = (updatedTask) => {
    setTasks(tasks.map(t => t.id === updatedTask.id ? updatedTask : t));
  };

  const handleTaskDeleted = (taskId) => {
    setTasks(tasks.filter(t => t.id !== taskId));
  };

  const filteredTasks = filter === 'all'
    ? tasks
    : tasks.filter(t => t.status === filter);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Project not found</h2>
          <button onClick={() => navigate('/dashboard')} className="btn-primary">
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center space-x-4 mb-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="text-gray-500 hover:text-gray-700 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
              <p className="text-gray-600 mt-1">{project.description}</p>
            </div>
            <span className={`badge ${
              project.status === 'active'
                ? 'bg-green-100 text-green-800'
                : 'bg-gray-100 text-gray-800'
            }`}>
              {project.status}
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Task Summary */}
        <div className="mb-8">
          <TaskSummary tasks={tasks} />
        </div>

        {/* Filter and Create Task Button */}
        <div className="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
          <div className="flex space-x-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                filter === 'all'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              All Tasks
            </button>
            <button
              onClick={() => setFilter('todo')}
              className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                filter === 'todo'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              To Do
            </button>
            <button
              onClick={() => setFilter('in_progress')}
              className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                filter === 'in_progress'
                  ? 'bg-yellow-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              In Progress
            </button>
            <button
              onClick={() => setFilter('done')}
              className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                filter === 'done'
                  ? 'bg-green-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              Done
            </button>
          </div>

          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-primary flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>New Task</span>
          </button>
        </div>

        {/* Task List */}
        <TaskList
          tasks={filteredTasks}
          onTaskUpdated={handleTaskUpdated}
          onTaskDeleted={handleTaskDeleted}
        />
      </main>

      {/* Create Task Modal */}
      {showCreateModal && (
        <CreateTaskModal
          projectId={parseInt(id)}
          onClose={() => setShowCreateModal(false)}
          onTaskCreated={handleTaskCreated}
        />
      )}
    </div>
  );
};

export default ProjectDetail;
