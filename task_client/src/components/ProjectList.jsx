import { Link } from 'react-router-dom';

const ProjectList = ({ projects, onRefresh }) => {
  if (projects.length === 0) {
    return (
      <div className="card text-center py-12">
        <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
        </svg>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No projects yet</h3>
        <p className="text-gray-500 mb-4">Get started by creating your first project</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {projects.map((project) => (
        <Link
          key={project.id}
          to={`/projects/${project.id}`}
          className="card hover:shadow-xl transition-all duration-200 cursor-pointer group"
        >
          <div className="flex items-start justify-between mb-3">
            <h3 className="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
              {project.name}
            </h3>
            <span className={`badge ${
              project.status === 'active'
                ? 'bg-green-100 text-green-800'
                : 'bg-gray-100 text-gray-800'
            }`}>
              {project.status}
            </span>
          </div>

          <p className="text-gray-600 text-sm mb-4 line-clamp-2">
            {project.description || 'No description'}
          </p>

          <div className="flex items-center justify-between text-xs text-gray-500 pt-4 border-t border-gray-100">
            <span>
              Created {new Date(project.created_at).toLocaleDateString()}
            </span>
            <svg className="w-5 h-5 text-primary-400 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </Link>
      ))}
    </div>
  );
};

export default ProjectList;
