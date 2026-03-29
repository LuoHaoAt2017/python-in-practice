# Sakila FastAPI + PostgreSQL Implementation

This project implements a FastAPI RESTful API for the Sakila sample database with PostgreSQL.

## Project Structure

```
python-in-practice/
├── api/                          # API endpoints
│   ├── endpoints/               # Individual endpoint modules
│   │   ├── actors.py           # Actor endpoints
│   │   ├── films.py            # Film endpoints
│   │   ├── customers.py        # Customer endpoints
│   │   ├── rentals.py          # Rental endpoints
│   │   └── health.py           # Health check endpoints
│   ├── router.py               # API router configuration
│   └── __init__.py
├── config/                      # Configuration
│   ├── settings.py             # Application settings
│   ├── database.py             # Database configuration
│   └── __init__.py
├── models/                      # SQLAlchemy ORM models
│   ├── actor.py                # Actor model
│   ├── film.py                 # Film model
│   ├── customer.py             # Customer model
│   ├── rental.py               # Rental model
│   ├── category.py             # Category model
│   ├── language.py             # Language model
│   ├── address.py              # Address model
│   ├── city.py                 # City model
│   ├── country.py              # Country model
│   ├── inventory.py            # Inventory model
│   ├── payment.py              # Payment model
│   ├── staff.py                # Staff model
│   ├── store.py                # Store model
│   ├── film_actor.py           # Film-Actor relationship
│   ├── film_category.py        # Film-Category relationship
│   ├── base.py                 # Base model with timestamps
│   └── __init__.py
├── schemas/                     # Pydantic schemas
│   ├── actor.py                # Actor schemas
│   ├── film.py                 # Film schemas
│   ├── customer.py             # Customer schemas
│   ├── rental.py               # Rental schemas
│   ├── category.py             # Category schemas
│   └── __init__.py
├── services/                    # Business logic
│   ├── actor.py                # Actor service
│   ├── film.py                 # Film service
│   ├── customer.py             # Customer service
│   ├── rental.py               # Rental service
│   └── __init__.py
├── test/                        # Unit tests (existing)
│   ├── test_students.py
│   └── student.py
├── main.py                      # FastAPI application
├── init_db.py                   # Database initialization script
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .env                         # Environment variables (auto-generated)
└── README_SAKILA.md            # This file
```

## Features

- **FastAPI** with async/await support
- **PostgreSQL** database with SQLAlchemy ORM
- **Asyncpg** for asynchronous database operations
- **Pydantic** for data validation and serialization
- **Comprehensive API endpoints** for Sakila entities:
  - Actors (CRUD operations with filtering)
  - Films (CRUD operations with filtering by title, year, rating, etc.)
  - Customers (CRUD operations with filtering)
  - Rentals (CRUD operations with return functionality)
- **Health checks** and database connectivity testing
- **CORS middleware** enabled
- **Environment-based configuration**

## Prerequisites

1. **Python 3.11+**
2. **PostgreSQL 12+** installed and running
3. **Git** (optional, for version control)

## Installation

### 1. Clone and navigate to the project
```bash
cd /Users/luohao/github/python-in-practice
```

### 2. Create and activate virtual environment
```bash
# Create virtual environment
python -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL

Make sure PostgreSQL is running with default credentials:
- Host: `localhost`
- Port: `5432`
- Username: `postgres`
- Password: `postgres`

If your PostgreSQL setup is different, update the `.env` file accordingly.

### 5. Initialize the database
```bash
python init_db.py
```

This script will:
- Check PostgreSQL connection
- Create the `sakila` database
- Create all tables using SQLAlchemy models
- Load test data (since official Sakila SQL files aren't included)

**Options for `init_db.py`:**
```bash
# Skip connection check (if PostgreSQL is already verified)
python init_db.py --skip-check

# Skip database creation (if database already exists)
python init_db.py --skip-create

# Skip table creation (if tables already exist)
python init_db.py --skip-tables

# Skip data loading
python init_db.py --skip-data

# Force re-initialization (not implemented but available for extension)
python init_db.py --force
```

### 6. Start the FastAPI server
```bash
python main.py
```

The server will start at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Swagger UI (Interactive API docs):** http://localhost:8000/docs
- **ReDoc (Alternative API docs):** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

## Available API Endpoints

### Health & System
- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /health/db` - Database health check

### Actors (`/api/v1/actors`)
- `GET /` - List actors with pagination and name filtering
- `GET /{actor_id}` - Get actor by ID
- `GET /{actor_id}/films` - Get actor with their films
- `POST /` - Create new actor
- `PUT /{actor_id}` - Update actor
- `DELETE /{actor_id}` - Delete actor

### Films (`/api/v1/films`)
- `GET /` - List films with pagination and filtering (title, year, rating, language)
- `GET /{film_id}` - Get film by ID
- `GET /{film_id}/actors` - Get film with its actors
- `GET /{film_id}/categories` - Get film with its categories
- `POST /` - Create new film
- `PUT /{film_id}` - Update film
- `DELETE /{film_id}` - Delete film

### Customers (`/api/v1/customers`)
- `GET /` - List customers with pagination and filtering (name, email, active status, store)
- `GET /{customer_id}` - Get customer by ID
- `GET /{customer_id}/rentals` - Get customer with rentals and payments
- `POST /` - Create new customer
- `PUT /{customer_id}` - Update customer
- `DELETE /{customer_id}` - Delete customer

### Rentals (`/api/v1/rentals`)
- `GET /` - List rentals with pagination and filtering (customer, inventory, staff, return status)
- `GET /{rental_id}` - Get rental by ID
- `GET /{rental_id}/details` - Get rental with film and customer details
- `POST /` - Create new rental
- `PUT /{rental_id}` - Update rental
- `PUT /{rental_id}/return` - Mark rental as returned
- `DELETE /{rental_id}` - Delete rental

## Environment Variables

Configuration is managed via environment variables in `.env` file:

```env
# PostgreSQL Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sakila
DATABASE_URL_ASYNC=postgresql+asyncpg://postgres:postgres@localhost:5432/sakila

# FastAPI Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your-secret-key-here-change-in-production
```

## Testing the API

### Using curl

```bash
# Get all actors
curl -X GET "http://localhost:8000/api/v1/actors/"

# Get actor by ID
curl -X GET "http://localhost:8000/api/v1/actors/1"

# Create a new actor
curl -X POST "http://localhost:8000/api/v1/actors/" \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Tom", "last_name": "Hanks"}'

# Get films with filtering
curl -X GET "http://localhost:8000/api/v1/films/?title=adventure&rating=PG-13"

# Create a rental
curl -X POST "http://localhost:8000/api/v1/rentals/" \
  -H "Content-Type: application/json" \
  -d '{"inventory_id": 1, "customer_id": 1, "staff_id": 1}'
```

### Using the Swagger UI

Navigate to `http://localhost:8000/docs` to:
- See all available endpoints
- Try them out directly in the browser
- View request/response schemas
- Test authentication (if implemented)

## Development

### Adding New Models

1. Create model in `models/` directory
2. Create schema in `schemas/` directory
3. Create service in `services/` directory
4. Create endpoints in `api/endpoints/` directory
5. Add router to `api/router.py`

### Database Migrations

For production, use Alembic migrations instead of `Base.metadata.create_all()`:

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migration
alembic upgrade head
```

### Testing

Run existing tests:
```bash
# Run unit tests
python -m pytest test/
```

## Troubleshooting

### PostgreSQL Connection Issues
1. Ensure PostgreSQL is running: `pg_isready` or `sudo systemctl status postgresql`
2. Check credentials in `.env` file
3. Verify database exists: `psql -U postgres -l`

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Module Import Errors
1. Make sure virtual environment is activated
2. Install dependencies: `pip install -r requirements.txt`
3. Check Python path: `echo $PYTHONPATH`

### Database Initialization Issues
1. Check PostgreSQL logs for errors
2. Try manual database creation:
```bash
psql -U postgres -c "CREATE DATABASE sakila;"
```
3. Run initialization steps separately using flags

## Next Steps & Enhancements

1. **Add Authentication** - JWT or OAuth2 for secure API access
2. **Implement Pagination** - More advanced pagination with cursors
3. **Add Caching** - Redis for frequently accessed data
4. **Implement Search** - Full-text search for films and actors
5. **Add GraphQL** - GraphQL endpoint alongside REST
6. **Dockerize** - Docker and Docker Compose for easy deployment
7. **CI/CD Pipeline** - Automated testing and deployment
8. **Monitoring** - Prometheus metrics and Grafana dashboards
9. **Rate Limiting** - Protect API from abuse
10. **WebSocket Support** - Real-time updates for rentals

## License

This project is for educational purposes as part of Python practice.

## Acknowledgments

- **Sakila Sample Database** - MySQL sample database for DVD rental stores
- **FastAPI** - Modern, fast web framework for building APIs with Python
- **SQLAlchemy** - SQL toolkit and Object-Relational Mapping (ORM) system
- **PostgreSQL** - Powerful, open source object-relational database system