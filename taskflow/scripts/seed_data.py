"""Seed the database with sample data for development and testing."""

import random
from datetime import datetime, timedelta

from taskflow.models.base import get_db, init_db
from taskflow.services.auth_service import AuthService
from taskflow.services.project_service import ProjectService
from taskflow.services.task_service import TaskService
from taskflow.utils.logger import get_logger

logger = get_logger(__name__)


def seed_database():
    """Seed the database with sample data."""
    logger.info("Starting database seeding...")

    # Initialize database
    init_db()

    with get_db() as db:
        auth_service = AuthService(db)
        project_service = ProjectService(db)
        task_service = TaskService(db)

        # Create 4 users
        logger.info("Creating users...")
        users = []
        user_data = [
            ("alice@example.com", "password123", "Alice Johnson"),
            ("bob@example.com", "password123", "Bob Smith"),
            ("carol@example.com", "password123", "Carol Williams"),
            ("josep@example.com", "password123", "Josep"),
        ]

        for email, password, name in user_data:
            user = auth_service.register_user(email=email, password=password, name=name)
            if user:
                users.append(user)
                logger.info(f"Created user: {email}")
            else:
                logger.warning(f"User {email} already exists")
                # Get existing user
                user = auth_service.user_repo.get_by_email(email)
                if user:
                    users.append(user)

        if not users:
            logger.error("No users created. Aborting seed.")
            return

        # Create 3 projects
        logger.info("Creating projects...")
        projects = []
        project_data = [
            ("Website Redesign", "Redesign company website with modern UI/UX", users[0].id),
            ("Mobile App Development", "Build iOS and Android mobile applications", users[1].id),
            ("API Migration", "Migrate REST API to GraphQL", users[2].id),
        ]

        for name, description, owner_id in project_data:
            project = project_service.create_project(
                name=name,
                owner_id=owner_id,
                description=description,
            )
            projects.append(project)
            logger.info(f"Created project: {name}")

        # Create tasks with various states
        logger.info("Creating tasks...")
        statuses = ["todo", "in_progress", "done", "blocked"]
        priorities = ["low", "medium", "high", "critical"]

        task_templates = [
            "Design homepage mockup",
            "Implement user authentication",
            "Write API documentation",
            "Set up CI/CD pipeline",
            "Create database schema",
            "Implement payment integration",
            "Write unit tests",
            "Conduct code review",
            "Deploy to production",
            "Update user documentation",
            "Fix login bug",
            "Optimize image loading",
            "Add search functionality",
            "Implement caching layer",
            "Refactor legacy code",
            "Add analytics tracking",
            "Security audit",
            "Performance testing",
            "Update dependencies",
            "Configure monitoring",
        ]

        task_count = 0
        # Create 20 tasks total, distributed across projects
        total_tasks = 20
        tasks_per_project = [7, 7, 6]  # Distribute 20 tasks across 3 projects

        for idx, project in enumerate(projects):
            num_tasks = tasks_per_project[idx]

            for i in range(num_tasks):
                # Random task attributes
                status = random.choice(statuses)
                priority = random.choice(priorities)
                assigned_to = random.choice([None, *[u.id for u in users[:3]]])

                # Random due date (some overdue, some future, some None)
                due_date_choice = random.choice(["past", "soon", "future", None])
                if due_date_choice == "past":
                    # Overdue by 1-10 days
                    due_date = datetime.utcnow() - timedelta(days=random.randint(1, 10))
                elif due_date_choice == "soon":
                    # Due within next 3 days
                    due_date = datetime.utcnow() + timedelta(days=random.randint(1, 3))
                elif due_date_choice == "future":
                    # Due in 4-30 days
                    due_date = datetime.utcnow() + timedelta(days=random.randint(4, 30))
                else:
                    due_date = None

                # Pick a random task template and modify it
                title = f"{random.choice(task_templates)} - {project.name[:20]}"

                description = f"Task for {project.name}. Priority: {priority}."
                if i % 3 == 0:
                    description += " This is a critical task that requires immediate attention."

                task = task_service.create_task(
                    project_id=project.id,
                    title=title,
                    description=description,
                    status=status,
                    priority=priority,
                    assigned_to=assigned_to,
                    due_date=due_date,
                )

                # Randomly add some comments
                if random.random() > 0.5:
                    task.comments_count = random.randint(0, 15)
                    db.commit()

                task_count += 1

        logger.info(f"Created {task_count} tasks across {len(projects)} projects")
        logger.info("✅ Database seeding completed successfully!")
        logger.info(f"\nCreated:")
        logger.info(f"  - {len(users)} users")
        logger.info(f"  - {len(projects)} projects")
        logger.info(f"  - {task_count} tasks")
        logger.info(f"\nSample credentials:")
        logger.info(f"  Email: alice@example.com")
        logger.info(f"  Password: password123")


if __name__ == "__main__":
    seed_database()
