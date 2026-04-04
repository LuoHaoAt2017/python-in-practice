# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI RESTful API for the Sakila sample database (DVD rental store) with PostgreSQL backend. The project implements CRUD operations for actors, films, customers, and rentals with a clean architecture.

## Architecture

### Core Structure
- `models/`: SQLAlchemy ORM models (23+ models mirroring Sakila schema)
- `schemas/`: Pydantic schemas for request/response validation
- `services/`: Business logic layer
- `api/endpoints/`: FastAPI route handlers organized by entity
- `config/`: Application configuration and database setup
- `tests/`: Test suite with comprehensive fixtures

### Database Configuration
- PostgreSQL with SQLAlchemy ORM and asyncpg for async operations
- Uses `sakila` schema in PostgreSQL (note the `search_path=sakila` in connection string)
- Dual engine setup: synchronous (`postgresql://`) for scripts, asynchronous (`postgresql+asyncpg://`) for API
- Connection configured via environment variables in `.env`

### API Design
- API prefix: `/api/v1`
- Standard CRUD endpoints for actors, films, customers, rentals
- Response formatting middleware in `api/middleware/response_formatter.py`
- CORS enabled for development
- Interactive docs at `/docs` when DEBUG=True

## Development Commands

### Setup & Initialization
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database (creates tables and loads test data)
python init_db.py

# Start development server
python main.py
```

### Database Management
```bash
# Initialize database with options
python init_db.py --skip-check      # Skip PostgreSQL connection check
python init_db.py --skip-create     # Skip database creation
python init_db.py --skip-tables     # Skip table creation
python init_db.py --skip-data       # Skip test data loading

# Access interactive API docs at http://localhost:8000/docs
```

### Testing
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_api.py

# Run with verbose output
python -m pytest tests/ -v

# Tests use SQLite in-memory database with comprehensive fixtures in `tests/conftest.py`
```

### Code Quality
```bash
# Format code with Black
black .

# Sort imports with isort
isort .
```

## Key Implementation Patterns

### Model Structure
- All models inherit from `models.base.Base` (includes `created_at` and `updated_at` timestamps)
- Foreign key relationships defined using SQLAlchemy's `relationship()` with explicit back_populates
- Composite primary keys used for junction tables (film_actor, film_category)

### Service Layer Pattern
- Each entity has corresponding service in `services/` directory
- Services handle database operations and business logic
- API endpoints call services rather than direct database operations

### Dependency Injection
- Database sessions injected via FastAPI dependencies (`get_async_db`)
- Configuration via Pydantic settings in `config.settings`

### Error Handling
- Uses FastAPI's built-in HTTPException for API errors
- Database errors caught and transformed to appropriate HTTP status codes

## Configuration Notes

### Environment Variables (`.env`)
- `DATABASE_URL`: Synchronous PostgreSQL connection (for scripts/migrations)
- `DATABASE_URL_ASYNC`: Async PostgreSQL connection (for FastAPI endpoints)
- `DEBUG`: Enable debug mode and interactive docs
- `HOST`, `PORT`: Server binding
- `SECRET_KEY`: Application secret (change in production)

### Database Connection Details
- PostgreSQL schema is `sakila`
- Default credentials: postgres:LuoHao@123 (URL-encoded in connection strings)
- In production, replace connection strings with secure credentials

## Testing Strategy

- Uses SQLite in-memory database for isolated testing
- Comprehensive fixtures create full test data hierarchy
- Async database operations supported via `pytest-asyncio`
- Test client provided for API endpoint testing

## Adding New Features

1. **Add new model**: Create in `models/` with proper relationships
2. **Add schemas**: Create request/response schemas in `schemas/`
3. **Add service**: Implement business logic in `services/`
4. **Add endpoints**: Create route handlers in `api/endpoints/`
5. **Register router**: Add to `api/router.py`
6. **Add tests**: Include in `tests/` with proper fixtures

## Important Notes

- Database tables auto-created in development (DEBUG=True) via `main.py` lifespan
- In production, use Alembic migrations instead of `Base.metadata.create_all()`
- Response middleware formats all API responses consistently
- Test data loaded by `init_db.py` includes representative sample data
- CORS is wide-open for development; restrict origins in production