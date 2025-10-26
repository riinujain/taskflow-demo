import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { projectsAPI, reportsAPI } from '../services/api';

const DailySummary = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [options, setOptions] = useState({
    include_overdue: true,
    include_assignees: true,
    compact: false,
  });

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const data = await projectsAPI.getAll();
      setProjects(data);
      if (data.length > 0) {
        setSelectedProject(data[0].id);
      }
    } catch (err) {
      console.error('Failed to load projects:', err);
      setError('Failed to load projects');
    }
  };

  const loadDailySummary = async () => {
    if (!selectedProject) return;

    try {
      setLoading(true);
      setError('');
      const data = await reportsAPI.getDailySummary(selectedProject, options);
      setSummary(data);
    } catch (err) {
      console.error('Failed to load daily summary:', err);
      setError(err.response?.data?.detail || 'Failed to load daily summary');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedProject) {
      loadDailySummary();
    }
  }, [selectedProject, options]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              </button>
              <h1 className="text-2xl font-bold text-gray-900">Daily Summary</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Welcome, <span className="font-medium text-gray-900">{user?.name}</span>
              </span>
              <button
                onClick={logout}
                className="btn-secondary"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        {/* Project Selector and Options */}
        <div className="card mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Report Options</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Project
              </label>
              <select
                value={selectedProject || ''}
                onChange={(e) => setSelectedProject(parseInt(e.target.value))}
                className="input-field"
              >
                <option value="">Select a project...</option>
                {projects.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex flex-wrap gap-4">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={options.include_overdue}
                onChange={(e) => setOptions({ ...options, include_overdue: e.target.checked })}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <span className="text-sm text-gray-700">Include Overdue Tasks</span>
            </label>

            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={options.include_assignees}
                onChange={(e) => setOptions({ ...options, include_assignees: e.target.checked })}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <span className="text-sm text-gray-700">Show Assignees</span>
            </label>

            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={options.compact}
                onChange={(e) => setOptions({ ...options, compact: e.target.checked })}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <span className="text-sm text-gray-700">Compact View</span>
            </label>
          </div>
        </div>

        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            <p className="mt-4 text-gray-600">Loading daily summary...</p>
          </div>
        )}

        {!loading && summary && (
          <div className="space-y-6">
            {/* Metrics Cards */}
            {summary.metrics && (
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="card text-center">
                  <p className="text-3xl font-bold text-gray-900">{summary.metrics.total_tasks}</p>
                  <p className="text-sm text-gray-600">Total Tasks</p>
                </div>
                <div className="card text-center bg-blue-50">
                  <p className="text-3xl font-bold text-blue-600">{summary.metrics.todo_count}</p>
                  <p className="text-sm text-blue-700">To Do</p>
                </div>
                <div className="card text-center bg-yellow-50">
                  <p className="text-3xl font-bold text-yellow-600">{summary.metrics.in_progress_count}</p>
                  <p className="text-sm text-yellow-700">In Progress</p>
                </div>
                <div className="card text-center bg-green-50">
                  <p className="text-3xl font-bold text-green-600">{summary.metrics.done_count}</p>
                  <p className="text-sm text-green-700">Done</p>
                </div>
                <div className="card text-center bg-red-50">
                  <p className="text-3xl font-bold text-red-600">{summary.metrics.blocked_count}</p>
                  <p className="text-sm text-red-700">Blocked</p>
                </div>
              </div>
            )}

            {/* Text Summary */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Summary Report</h3>
              <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                <pre className="whitespace-pre-wrap font-mono text-sm text-gray-800 leading-relaxed">
                  {summary.text_summary}
                </pre>
              </div>
            </div>
          </div>
        )}

        {!loading && !summary && selectedProject && (
          <div className="card text-center py-12">
            <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No summary available</h3>
            <p className="text-gray-500">Select a project to view its daily summary</p>
          </div>
        )}
      </main>
    </div>
  );
};

export default DailySummary;
