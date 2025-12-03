# Convey Backend

FastAPI backend for the Convey document summarization application.

## Features

- FastAPI REST API with async support
- PostgreSQL database with SQLAlchemy ORM
- JWT authentication
- Document processing and AI-powered summarization
- OpenAI and Gemini provider support
- Alembic database migrations
- Docker-based local development

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd convey-backend
   ```

2. **Install dependencies:**
   ```bash
   # Using uv (recommended)
   uv sync

   # Or using pip
   python -m venv .venv
   source .venv/bin/activate
   pip install .
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and set:
   # - OPENAI_API_KEY
   # - JWT_SECRET_KEY (generate with: openssl rand -hex 32)
   ```

4. **Start local database:**
   ```bash
   docker-compose up -d
   ```

5. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

6. **(Optional) Seed test data:**
   ```bash
   python scripts/seed-local-db.py
   ```

## Database Setup

### Local Development with Docker

This project uses PostgreSQL. For local development, we provide a Docker setup:

```bash
# Start local PostgreSQL database
docker-compose up -d

# Run database migrations
alembic upgrade head

# (Optional) Seed with test data
python scripts/seed-local-db.py
```

The backend automatically connects to the local Docker database when `DB_ENVIRONMENT=local` (default).

### Environment Switching

- **Local:** `DB_ENVIRONMENT=local` (default) - Docker PostgreSQL
- **Production:** `DB_ENVIRONMENT=production` - Supabase cloud database

To test against production:
```bash
echo "DB_ENVIRONMENT=production" > .env.local
# Add PRODUCTION_DATABASE_URL to .env.local
```

### Quick Reset

Reset your local database:
```bash
./scripts/reset-local-db.sh
```

See [Database Setup Guide](docs/DATABASE_SETUP.md) for detailed instructions, troubleshooting, and production deployment.

## Running Locally

Start the development server:

```bash
python main.py
# or using uv:
uv run main.py
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

When you make changes to your project, the server will automatically reload.

## API Endpoints

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user
- `GET /api/v1/projects` - List projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects/{id}` - Get project details
- `POST /api/v1/projects/{id}/documents` - Upload document
- `GET /api/v1/projects/{id}/documents` - List documents
- `POST /api/v1/projects/{id}/summaries` - Create summary
- `GET /api/v1/projects/{id}/summaries` - List summaries
- `GET /api/v1/health` - Health check

## Deploying to Vercel

### Prerequisites

Set environment variables in Vercel dashboard:
- `DB_ENVIRONMENT=production`
- `PRODUCTION_DATABASE_URL=<supabase-url>`
- `OPENAI_API_KEY=<your-key>`
- `JWT_SECRET_KEY=<your-secret>`
- `CORS_ORIGINS=<frontend-url>`

### Deploy

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

Or use the Vercel Git integration for automatic deployments.

**Important:** Run database migrations before deploying:
```bash
export DB_ENVIRONMENT=production
export PRODUCTION_DATABASE_URL="<supabase-url>"
alembic upgrade head
```

## Project Structure

```
.
├── alembic/              # Database migration scripts
├── app/
│   ├── api/              # API routes and dependencies
│   │   └── routes/       # Endpoint handlers
│   ├── models/           # Database and request/response models
│   ├── repositories/     # Database access layer
│   ├── services/         # Business logic (auth, AI providers)
│   ├── config.py         # Application configuration
│   ├── database.py       # Database connection setup
│   └── main.py           # FastAPI application
├── docs/                 # Documentation
├── scripts/              # Utility scripts (seed, reset)
├── docker-compose.yml    # Local PostgreSQL setup
├── main.py               # Application entry point
└── pyproject.toml        # Python dependencies
```

## Development

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check status
alembic current
```

### Testing

```bash
# Run tests (when available)
pytest

# Run with coverage
pytest --cov=app
```

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL (Supabase)
- **ORM:** SQLAlchemy 2.0 (async)
- **Migrations:** Alembic
- **Authentication:** JWT (python-jose)
- **Password Hashing:** passlib (bcrypt)
- **AI Providers:** OpenAI, Google Gemini
- **Deployment:** Vercel (serverless functions)

## License

MIT

## Support

For detailed database setup, troubleshooting, and production deployment instructions, see [Database Setup Guide](docs/DATABASE_SETUP.md).
