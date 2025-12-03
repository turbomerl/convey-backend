-- Initialize database extensions for Convey
-- This script runs automatically when the Docker PostgreSQL container is created

-- Enable UUID extension for PostgreSQL
-- Required for UUID primary keys in our database models
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Database 'convey' is automatically created by Docker (see POSTGRES_DB in docker-compose.yml)
-- Tables will be created by Alembic migrations (run: alembic upgrade head)
