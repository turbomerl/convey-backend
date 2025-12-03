#!/bin/bash
# Reset local development database
# This script stops the database, removes all data, starts fresh, runs migrations, and optionally seeds test data

set -e  # Exit on any error

echo "🔄 Resetting local database..."
echo

# Stop and remove containers and volumes
echo "📦 Stopping and removing Docker containers..."
docker-compose down -v

# Start fresh database
echo "🚀 Starting fresh PostgreSQL container..."
docker-compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 5

# Verify database is ready
echo "🔍 Verifying database connection..."
until docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; do
    echo "   Still waiting..."
    sleep 2
done
echo "✅ Database is ready!"
echo

# Run migrations
echo "📝 Running database migrations..."
alembic upgrade head
echo

# Seed database (optional)
read -p "🌱 Seed database with test data? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python scripts/seed-local-db.py
else
    echo "⏭️  Skipping database seeding"
fi

echo
echo "✅ Local database reset complete!"
echo
echo "Database connection string:"
echo "  postgresql://postgres:postgres@localhost:5432/convey"
echo
echo "To access PostgreSQL CLI:"
echo "  docker-compose exec postgres psql -U postgres -d convey"
