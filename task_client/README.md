# TaskFlow Client

Beautiful and modern React frontend for the TaskFlow task management system.

## Features

- 🔐 **Authentication** - Secure login and registration with JWT
- 📊 **Dashboard** - Overview of all projects with statistics
- 📁 **Project Management** - Create and manage projects
- ✅ **Task Management** - Create, update, and track tasks
- 🎨 **Modern UI** - Clean design with Tailwind CSS
- 📱 **Responsive** - Works on desktop, tablet, and mobile

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first CSS framework

## Prerequisites

- Node.js 16+ and npm
- TaskFlow backend API running on `http://localhost:8000`

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The application will open at `http://localhost:3000`

### 3. Build for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

## Project Structure

```
task_client/
├── src/
│   ├── components/         # Reusable React components
│   │   ├── CreateProjectModal.jsx
│   │   ├── CreateTaskModal.jsx
│   │   ├── ProjectList.jsx
│   │   ├── TaskList.jsx
│   │   └── TaskSummary.jsx
│   ├── context/           # React Context providers
│   │   └── AuthContext.jsx
│   ├── pages/             # Page components
│   │   ├── Dashboard.jsx
│   │   ├── Login.jsx
│   │   ├── ProjectDetail.jsx
│   │   └── Register.jsx
│   ├── services/          # API service layer
│   │   └── api.js
│   ├── App.jsx            # Main app component with routing
│   ├── main.jsx           # Entry point
│   └── index.css          # Global styles with Tailwind
├── public/                # Static assets
├── index.html             # HTML template
├── package.json           # Dependencies
├── tailwind.config.js     # Tailwind configuration
├── vite.config.js         # Vite configuration
└── README.md
```

## Available Scripts

- `npm run dev` - Start development server on port 3000
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

## Usage Guide

### Login

Use one of the seeded accounts:
- **Email:** `alice@example.com`
- **Password:** `password123`

Or create a new account via the registration page.

### Dashboard

After logging in, you'll see:
- **Statistics cards** showing total projects, active projects, and total tasks
- **Project list** with cards for each project
- **New Project button** to create projects

### Project Management

Click on any project card to view:
- **Task summary** with counts by status
- **Task filters** to view tasks by status (All, To Do, In Progress, Done)
- **Task list** with inline status updates
- **New Task button** to create tasks

### Task Management

Each task displays:
- Title and description
- Priority badge (Low, Medium, High, Critical)
- Status dropdown for quick updates
- Due date (if set)
- Delete button

Update task status by clicking the dropdown and selecting a new status.

## API Configuration

The API base URL is configured in `src/services/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

To change the backend URL, update this value.

## Authentication

- JWT tokens are stored in `localStorage`
- Tokens are automatically included in API requests via Axios interceptors
- Expired or invalid tokens trigger automatic logout and redirect to login

## Styling

This project uses Tailwind CSS with custom utility classes defined in `src/index.css`:

- `.btn-primary` - Primary action button
- `.btn-secondary` - Secondary action button
- `.btn-danger` - Destructive action button
- `.input-field` - Form input field
- `.card` - Content card with shadow
- `.badge` - Small label badge

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development

### Hot Module Replacement

Vite provides instant HMR for fast development. Changes to React components will reflect immediately without losing state.

### Adding New Features

1. Create components in `src/components/`
2. Create pages in `src/pages/`
3. Add API methods in `src/services/api.js`
4. Update routes in `src/App.jsx`

## Troubleshooting

### API Connection Errors

- Ensure the backend is running on `http://localhost:8000`
- Check browser console for CORS errors
- Verify the API base URL in `src/services/api.js`

### Build Errors

- Clear `node_modules` and reinstall: `rm -rf node_modules package-lock.json && npm install`
- Clear Vite cache: `rm -rf node_modules/.vite`

### Authentication Issues

- Clear localStorage: Open DevTools > Application > Local Storage > Clear
- Check JWT token expiration (60 minutes by default)

## License

This project is part of the TaskFlow demo application.
