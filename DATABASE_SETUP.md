# Database Setup Guide

This guide covers setting up the PostgreSQL database for the Football Simulation application using Docker.

## Prerequisites

- Docker and Docker Compose installed
- Git (to clone the repository)

## Quick Start

1. **Copy environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Start the database**:
   ```bash
   docker-compose up postgres -d
   ```

3. **Verify database is running**:
   ```bash
   docker-compose ps
   ```

4. **Connect to database** (optional):
   ```bash
   docker exec -it football-sim-postgres psql -U football_user -d football_sim
   ```

## Development Setup

### Starting Services

**Database only** (for local Python development):
```bash
docker-compose up postgres -d
```

**Full stack** (database + backend):
```bash
docker-compose --profile full-stack up -d
```

### Database Management

**View logs**:
```bash
docker-compose logs postgres
```

**Stop services**:
```bash
docker-compose down
```

**Reset database** (destroys all data):
```bash
docker-compose down -v
docker-compose up postgres -d
```

### Test Database

For running tests with a separate database:
```bash
docker-compose up postgres-test -d
```

## Database Connection Details

### Development Database
- **Host**: localhost
- **Port**: 5432
- **Database**: football_sim
- **Username**: football_user
- **Password**: football_dev_password
- **Connection URL**: `postgresql://football_user:football_dev_password@localhost:5432/football_sim`

### Test Database
- **Host**: localhost
- **Port**: 5433
- **Database**: football_sim_test
- **Username**: football_test_user
- **Password**: football_test_password
- **Connection URL**: `postgresql://football_test_user:football_test_password@localhost:5433/football_sim_test`

## Schema Management

The database schema is automatically created when the container starts using the SQL files in `/database/init/`.

### Manual Schema Updates

If you need to manually update the schema:

1. Connect to the database:
   ```bash
   docker exec -it football-sim-postgres psql -U football_user -d football_sim
   ```

2. Run your SQL commands directly in the PostgreSQL prompt.

### Backing Up Data

**Create backup**:
```bash
docker exec football-sim-postgres pg_dump -U football_user football_sim > backup.sql
```

**Restore backup**:
```bash
cat backup.sql | docker exec -i football-sim-postgres psql -U football_user -d football_sim
```

## Production Deployment

For production deployment on Azure:

1. Update the `docker-compose.yml` with production environment variables
2. Use secure passwords (not the development defaults)
3. Mount persistent volumes for data storage
4. Consider using Azure Database for PostgreSQL if preferred

### Azure Container Instances

Example Azure deployment:
```bash
# Create resource group
az group create --name football-sim-rg --location eastus

# Deploy container group
az container create \
  --resource-group football-sim-rg \
  --name football-sim-app \
  --file docker-compose.yml
```

## Troubleshooting

### Common Issues

**Connection refused**:
- Ensure Docker is running
- Check if port 5432 is already in use
- Verify firewall settings

**Database doesn't exist**:
- Check container logs: `docker-compose logs postgres`
- Ensure initialization scripts ran successfully

**Permission denied**:
- Verify volume permissions
- Check that Docker has access to the project directory

### Health Checks

Check database health:
```bash
docker-compose exec postgres pg_isready -U football_user -d football_sim
```

### Performance Monitoring

View active connections:
```sql
SELECT * FROM pg_stat_activity;
```

Check database size:
```sql
SELECT pg_size_pretty(pg_database_size('football_sim'));
```

## Environment Variables

Key environment variables (set in `.env`):

- `DATABASE_URL`: Full database connection string
- `DATABASE_TEST_URL`: Test database connection string
- `POSTGRES_DB`: Database name
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password

## Next Steps

After setting up the database:

1. Install Python dependencies: `pip install -r backend/requirements.txt`
2. Run database migrations (when implemented)
3. Seed the database with team data
4. Start the Flask application

See the main README for full application setup instructions.