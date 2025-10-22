.PHONY: dev install lint fmt typecheck test seed clean setup-db

# Run development server with hot reload
dev:
	uvicorn taskflow.main:app --reload

# Install dependencies
install:
	pip install -e ".[dev]"

# Run linter
lint:
	ruff check .

# Format code (ruff + black)
fmt:
	ruff check --fix . && black .

# Type check with mypy
typecheck:
	mypy taskflow

# Run tests (quiet mode)
test:
	pytest -q

# Seed database with sample data
seed:
	python -m taskflow.scripts.seed_data

# Clean database and cache files
clean:
	rm -f taskflow.db
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Initialize database tables
setup-db:
	python -c "from taskflow.models.base import init_db; init_db()"
