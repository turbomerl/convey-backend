# Database Setup Guide

Complete guide for setting up and managing the PostgreSQL database for local development and production.

## Table of Contents

- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Local Development](#local-development)
- [Environment Switching](#environment-switching)
- [Common Tasks](#common-tasks)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)
- [Docker Commands Reference](#docker-commands-reference)

## Quick Start

### Local Development (Default)

1. **Start Docker PostgreSQL:**
   ```bash
   docker-compose up -d
   ```

2. **Set environment to local** (default, no action needed):
   ```bash
   # Optional: Create .env.local to explicitly set
   echo "DB_ENVIRONMENT=local" > .env.local
   ```

3. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

4. **(Optional) Seed test data:**
   ```bash
   python scripts/seed-local-db.py
   ```

5. **Start backend:**
   ```bash
   python main.py
   ```

Your local development database is now ready! The backend will connect to PostgreSQL running in Docker at `localhost:5432`.

### Quick Reset

To reset your local database and start fresh:

```bash
./scripts/reset-local-db.sh
```

This will:
- Stop and remove the database container
- Delete all data
- Start a fresh database
- Run migrations
- Optionally seed test data

## Architecture

### Environment-Based Configuration

The backend supports two database environments controlled by the `DB_ENVIRONMENT` variable:

| Environment | Value | Database | Usage |
|-------------|-------|----------|-------|
| **Local** | `local` | Docker PostgreSQL (`localhost:5432`) | Development (default) |
| **Production** | `production` | Supabase Cloud | Production deployment |

### Configuration Precedence

Settings are loaded in this order (later overrides earlier):

1. **Default values** in `app/config.py` (lowest priority)
2. **`.env` file** (committed to git, shared defaults)
3. **`.env.local` file** (gitignored, personal overrides - highest priority)

Example:
- `.env` has `DB_ENVIRONMENT=local` (default for all developers)
- Create `.env.local` with `DB_ENVIRONMENT=production` to test against production
- Your `.env.local` won't be committed, so it won't affect other developers

### Database URLs

**Local (Docker):**
```
postgresql+asyncpg://postgres:postgres@localhost:5432/convey
```

**Production (Supabase):**
```
postgresql+asyncpg://user:pass@aws-0-us-east-1.pooler.supabase.com:6543/postgres?ssl=require
```

## Local Development

### Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ with uv or pip
- Alembic migrations tool

### Initial Setup

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
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # Copy example file
   cp .env.example .env

   # Edit .env and set required values:
   # - OPENAI_API_KEY
   # - JWT_SECRET_KEY (generate with: openssl rand -hex 32)
   ```

4. **Start local database:**
   ```bash
   docker-compose up -d
   ```

5. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Seed test data (optional):**
   ```bash
   python scripts/seed-local-db.py
   ```

You're now ready to develop!

### Daily Development Workflow

**Start working:**
```bash
# Start database (if not running)
docker-compose up -d

# Start backend
python main.py
```

**Stop working:**
```bash
# Stop backend: Ctrl+C

# Stop database (optional, or leave running)
docker-compose stop
```

**View logs:**
```bash
# Backend logs: visible in terminal

# Database logs:
docker-compose logs -f postgres
```

## Environment Switching

### Switch to Production Database

To test against the production Supabase database:

#### Option 1: Using .env.local (Recommended)

1. **Create `.env.local` file:**
   ```bash
   cat > .env.local << EOF
   DB_ENVIRONMENT=production
   PRODUCTION_DATABASE_URL=postgresql+asyncpg://user:pass@host:6543/db?ssl=require
   EOF
   ```

2. **Restart backend** - it will now connect to production

#### Option 2: Inline Environment Variable

```bash
DB_ENVIRONMENT=production PRODUCTION_DATABASE_URL="postgresql+asyncpg://..." python main.py
```

### Switch Back to Local

**Delete or modify `.env.local`:**

```bash
# Option 1: Delete file
rm .env.local

# Option 2: Change environment
echo "DB_ENVIRONMENT=local" > .env.local
```

## Common Tasks

### Create a New Migration

When you modify database models:

```bash
# 1. Make changes to app/models/database.py

# 2. Generate migration
alembic revision --autogenerate -m "describe your changes"

# 3. Review the generated migration in alembic/versions/

# 4. Apply migration
alembic upgrade head
```

### Rollback Migration

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base

# Re-apply migrations
alembic upgrade head
```

### Check Migration Status

```bash
# Show current migration version
alembic current

# Show migration history
alembic history

# Show migration history with details
alembic history --verbose
```

### Backup Local Database

```bash
# Backup to file
docker-compose exec postgres pg_dump -U postgres convey > backup-$(date +%Y%m%d-%H%M%S).sql

# View backup
less backup-*.sql
```

### Restore from Backup

```bash
# Reset database first
./scripts/reset-local-db.sh

# Restore from backup file
docker-compose exec -T postgres psql -U postgres convey < backup-20240101-120000.sql
```

### Access PostgreSQL CLI

```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d convey

# Example queries:
\dt                    # List tables
\d users               # Describe users table
SELECT * FROM users;   # Query users
\q                     # Quit
```

### View Current Configuration

```python
# Run Python shell in backend environment
python

# Check database configuration
from app.config import settings
print(f"Environment: {settings.db_environment}")
print(f"Database URL: {settings.get_database_url()}")
print(f"Is Local: {settings.is_local_db}")
print(f"Is Production: {settings.is_production_db}")
```

## Troubleshooting

### "Connection refused" Error

**Symptom:**
```
Connection refused: localhost:5432
```

**Cause:** Docker PostgreSQL not running

**Solution:**
```bash
# Check if container is running
docker-compose ps

# If not running, start it
docker-compose up -d

# Wait a few seconds and try again
sleep 5
```

### "Database does not exist" Error

**Symptom:**
```
database "convey" does not exist
```

**Cause:** Fresh PostgreSQL instance without database creation

**Solution:**
```bash
# The database should be auto-created by Docker
# If not, reset the container:
docker-compose down -v
docker-compose up -d
sleep 5
alembic upgrade head
```

### "Table does not exist" Error

**Symptom:**
```
relation "users" does not exist
```

**Cause:** Migrations not applied

**Solution:**
```bash
# Check migration status
alembic current

# Apply migrations
alembic upgrade head
```

### "Invalid db_environment" Error

**Symptom:**
```
ValueError: Invalid db_environment: Local
```

**Cause:** Typo in environment variable (case-sensitive)

**Solution:**
```bash
# Correct values are lowercase: "local" or "production"
echo "DB_ENVIRONMENT=local" > .env.local
```

### Docker Container Won't Start

**Symptom:**
```
Error: port 5432 is already in use
```

**Cause:** Another PostgreSQL instance using port 5432

**Solution:**
```bash
# Option 1: Stop other PostgreSQL instance
# On macOS:
brew services stop postgresql

# Option 2: Change port in docker-compose.yml
# Edit: "5433:5432" instead of "5432:5432"
# Then update LOCAL_DB_PORT=5433 in .env
```

### "Production database URL not configured" Error

**Symptom:**
```
ValueError: Production database URL not configured
```

**Cause:** `DB_ENVIRONMENT=production` but no production URL set

**Solution:**
```bash
# Add production URL to .env.local
echo "PRODUCTION_DATABASE_URL=postgresql+asyncpg://..." >> .env.local
```

### Alembic Migration Conflict

**Symptom:**
```
Multiple head revisions detected
```

**Cause:** Two developers created migrations simultaneously

**Solution:**
```bash
# Create a merge migration
alembic merge heads -m "merge migrations"

# Apply the merge
alembic upgrade head
```

## Production Deployment

### Vercel Environment Variables

Set these in the Vercel Dashboard under **Settings → Environment Variables**:

```bash
DB_ENVIRONMENT=production
PRODUCTION_DATABASE_URL=<supabase-connection-string>
OPENAI_API_KEY=<your-openai-key>
JWT_SECRET_KEY=<your-jwt-secret>
CORS_ORIGINS=https://your-frontend.vercel.app
```

**Important:**
- Never commit production credentials to git
- Use Vercel's encrypted environment variables
- Production URL must include `?ssl=require` parameter

### Running Production Migrations

Migrations should be run manually before deploying code changes:

```bash
# 1. Set production environment locally
export DB_ENVIRONMENT=production
export PRODUCTION_DATABASE_URL="<supabase-url>"

# 2. Run migrations
alembic upgrade head

# You'll be prompted to confirm:
# ⚠️  WARNING: Running migrations against PRODUCTION database!
#    Database: aws-0-us-east-1.pooler.supabase.com:6543
#    Continue? (yes/no):

# 3. Type "yes" to proceed

# 4. Deploy to Vercel
vercel --prod
```

**Never run migrations from Vercel functions** - they're stateless and could cause conflicts.

### Production Safety Checklist

Before running production migrations:

- [ ] Test migration on local database first
- [ ] Review migration SQL in `alembic/versions/` file
- [ ] Verify migration is reversible (has `downgrade()`)
- [ ] Backup production database (Supabase does this automatically)
- [ ] Run during low-traffic period if possible
- [ ] Monitor application after migration

### Automated Confirmation

For CI/CD pipelines, you can skip the interactive prompt:

```bash
export ALEMBIC_PRODUCTION_CONFIRMED=true
export DB_ENVIRONMENT=production
export PRODUCTION_DATABASE_URL="..."
alembic upgrade head
```

**Use with caution** - only in trusted CI/CD environments.

## Docker Commands Reference

### Basic Operations

```bash
# Start database
docker-compose up -d

# Stop database (keep data)
docker-compose stop

# Start stopped database
docker-compose start

# Stop and remove container (keep data)
docker-compose down

# Stop and delete all data
docker-compose down -v

# View logs
docker-compose logs -f postgres

# View running containers
docker-compose ps
```

### Database Operations

```bash
# Access PostgreSQL CLI
docker-compose exec postgres psql -U postgres -d convey

# Run SQL file
docker-compose exec -T postgres psql -U postgres -d convey < script.sql

# Dump database
docker-compose exec postgres pg_dump -U postgres convey > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres convey < backup.sql

# Check database size
docker-compose exec postgres psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('convey'));"
```

### Maintenance

```bash
# View disk usage
docker system df

# Clean up unused Docker resources
docker system prune

# Rebuild container (if docker-compose.yml changed)
docker-compose up -d --build

# View container resource usage
docker stats convey-postgres
```

### Troubleshooting

```bash
# Check if database is ready
docker-compose exec postgres pg_isready -U postgres

# View PostgreSQL version
docker-compose exec postgres psql -U postgres -c "SELECT version();"

# Check active connections
docker-compose exec postgres psql -U postgres -c "SELECT * FROM pg_stat_activity;"

# Kill stuck connections
docker-compose exec postgres psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='convey' AND pid <> pg_backend_pid();"
```

## Best Practices

### Do's ✅

- **Use .env.local for personal overrides** - Never commit it
- **Reset database regularly** - Keeps migrations tested
- **Test migrations locally first** - Before production
- **Back up before major changes** - Use pg_dump
- **Use descriptive migration names** - Future you will thank you
- **Review auto-generated migrations** - Alembic isn't perfect
- **Keep migrations small and focused** - One concept per migration

### Don'ts ❌

- **Don't commit .env.local** - It's gitignored for a reason
- **Don't edit applied migrations** - Create a new one instead
- **Don't use `--no-verify` with Alembic** - Safety checks are there for a reason
- **Don't run migrations in production without review** - Always check the SQL first
- **Don't keep old backup files in the repo** - They get huge
- **Don't use production DB for development** - Use local Docker
- **Don't skip migrations** - Apply them in order

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Supabase Documentation](https://supabase.com/docs)

## Support

If you encounter issues not covered in this guide:

1. Check the [Troubleshooting](#troubleshooting) section
2. Search existing issues in the repository
3. Ask in the team chat or create an issue
4. Include relevant error messages and commands you ran

---

Last updated: December 2024
