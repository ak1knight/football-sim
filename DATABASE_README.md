# PostgreSQL Database Implementation for Football Simulation

This document provides a comprehensive guide to the PostgreSQL database implementation for the Football Simulation application, including setup, architecture, and usage instructions.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js (for frontend)

### 1. Database Setup
```bash
# Copy environment configuration
cp .env.example .env

# Start PostgreSQL database
docker-compose up postgres -d

# Install Python dependencies
cd backend
pip install -r requirements.txt

# Initialize database schema
python manage_db.py init

# Verify database setup
python manage_db.py verify

# Seed with NFL teams and players
python manage_db.py seed
```

### 2. Development Environment
```bash
# Start full development stack
docker-compose --profile full-stack up -d

# Or run backend locally with database in Docker
docker-compose up postgres -d
cd backend && python app.py
```

## 📊 Database Architecture

### Schema Design
Our PostgreSQL database follows a user-centric, multi-tenant architecture:

```
Users (Authentication & Profiles)
├── User Leagues (Custom Leagues)
├── Seasons (User-owned Seasons)
│   ├── Season Teams (Team Records)
│   ├── Season Games (Game Results)
│   └── Playoff Brackets (Tournament Data)
└── User Sessions (Authentication)

Teams (NFL Team Data)
├── Players (Team Rosters)
└── Game Stats (Performance Data)
```

### Key Features
- **User Isolation**: Each user owns their seasons and data
- **JSONB Storage**: Flexible statistics and game data storage
- **UUID Primary Keys**: Globally unique identifiers
- **Automatic Timestamps**: Created/updated tracking
- **Foreign Key Constraints**: Data integrity enforcement

## 🛠️ Implementation Components

### ✅ Completed Components

#### Infrastructure
- **Docker Configuration**: PostgreSQL containers for development and testing
- **Environment Management**: Configuration via environment variables
- **Connection Pooling**: SQLAlchemy Core with connection management
- **Migration System**: Schema versioning and deployment

#### Database Schema
- **Complete Table Definitions**: All entities with proper relationships
- **Indexes and Constraints**: Performance and data integrity
- **Custom Types**: PostgreSQL ENUMs for status fields
- **Triggers**: Automatic timestamp updates

#### Data Access Layer
- **Base DAO Classes**: Common CRUD operations with error handling
- **Entity-Specific DAOs**: UserDAO, TeamDAO, PlayerDAO
- **Type Safety**: Full Python type hints
- **Transaction Management**: Automatic rollback on errors

#### Tools and Scripts
- **CLI Management**: `manage_db.py` for database operations
- **Seed Data System**: NFL teams and players population
- **Health Checks**: Database connection and schema verification

### 🔧 Available Commands

#### Database Management
```bash
# Schema operations
python manage_db.py init [--force]    # Initialize database schema
python manage_db.py verify             # Verify schema integrity
python manage_db.py drop --confirm     # Drop all schema objects

# Data operations
python manage_db.py seed [--force]     # Populate with NFL data
python manage_db.py status             # Show database status
python manage_db.py test               # Test database connection
```

#### Docker Operations
```bash
# Database only
docker-compose up postgres -d

# Full stack (backend + database)
docker-compose --profile full-stack up -d

# View logs
docker-compose logs postgres

# Reset database
docker-compose down -v
```

## 📁 File Structure

```
backend/
├── database/
│   ├── __init__.py              # Database package
│   ├── connection.py            # Connection management
│   ├── schema.py                # SQLAlchemy table definitions
│   ├── migrations.py            # Migration system
│   ├── seed_data.py             # Data seeding utilities
│   └── dao/                     # Data Access Objects
│       ├── __init__.py          # DAO package
│       ├── base.py              # Base DAO classes
│       ├── user_dao.py          # User operations
│       ├── team_dao.py          # Team operations
│       └── player_dao.py        # Player operations
├── manage_db.py                 # CLI management script
├── requirements.txt             # Python dependencies
└── Dockerfile                   # Container configuration

docker-compose.yml               # PostgreSQL containers
.env.example                     # Environment template
DATABASE_SETUP.md               # Setup instructions
DATABASE_IMPLEMENTATION_PROGRESS.md  # Implementation status
```

## 🏗️ Data Access Patterns

### Basic Operations
```python
from database import get_db_manager
from database.dao import TeamDAO, UserDAO

# Initialize
db_manager = get_db_manager()
team_dao = TeamDAO(db_manager)
user_dao = UserDAO(db_manager)

# Create operations
user_id = user_dao.create_user("john_doe", "john@example.com", "password123")
team = team_dao.get_by_abbreviation("KC")

# Query operations
afc_teams = team_dao.get_by_conference("AFC")
user = user_dao.authenticate_user("john_doe", "password123")

# Update operations
team_dao.update_team_stats(team['id'], {"offensive_rating": 95})
user_dao.update_profile(user_id, {"first_name": "John"})
```

### Transaction Management
```python
# Automatic transaction handling
with db_manager.get_db_transaction() as conn:
    # Multiple operations in single transaction
    conn.execute(insert(teams_table).values(...))
    conn.execute(update(players_table).values(...))
    # Auto-commit on success, auto-rollback on error
```

## 🔐 Security Features

### Authentication
- **Password Hashing**: bcrypt with salt for secure password storage
- **User Sessions**: JWT token management with database tracking
- **Row-Level Security**: Users can only access their own data

### Data Protection
- **SQL Injection Prevention**: Parameterized queries throughout
- **Input Validation**: Type checking and constraint enforcement
- **Connection Security**: Encrypted connections in production

## 🚀 Next Steps

### Immediate (Ready to Implement)
1. **API Integration**: Update Flask endpoints to use database DAOs
2. **Authentication System**: Implement JWT-based user authentication
3. **Season Management**: Create SeasonDAO and related game DAOs
4. **Testing Framework**: Add database test utilities

### Medium-term
1. **Performance Optimization**: Add database indexes for common queries
2. **Backup System**: Automated database backup and restore
3. **Monitoring**: Database performance and health monitoring
4. **API Documentation**: Update API docs for database integration

### Long-term
1. **Azure Deployment**: Production database configuration
2. **Scaling**: Read replicas and connection pooling optimization
3. **Analytics**: Reporting and data analysis capabilities
4. **Advanced Features**: Real-time updates, caching layer

## 📊 Performance Considerations

### Indexes
- **Primary Keys**: Automatic UUID indexes
- **Foreign Keys**: Automatic relationship indexes  
- **Search Fields**: Username, email, team abbreviation
- **JSONB Fields**: GIN indexes for complex queries

### Query Optimization
- **Connection Pooling**: 10 base connections, 20 overflow
- **Statement Caching**: Prepared statement reuse
- **Bulk Operations**: Batch inserts for large datasets
- **Lazy Loading**: On-demand relationship loading

## 🧪 Testing Strategy

### Database Testing
```python
# Test database setup
pytest backend/tests/test_database/

# Integration tests with test database
DATABASE_TEST_URL=postgresql://...test_db pytest

# Performance testing
python backend/test_performance.py
```

### Docker Testing
```bash
# Start test database
docker-compose up postgres-test -d

# Run tests against test database
export DATABASE_URL=postgresql://football_test_user:football_test_password@localhost:5433/football_sim_test
python -m pytest backend/tests/
```

## 🔧 Troubleshooting

### Common Issues
1. **Connection Refused**: Ensure Docker is running and ports are available
2. **Schema Errors**: Run `python manage_db.py verify` to check schema
3. **Permission Denied**: Check Docker permissions and file ownership
4. **Import Errors**: Ensure all dependencies are installed

### Debug Commands
```bash
# Check database status
python manage_db.py status

# View container logs
docker-compose logs postgres

# Connect to database directly
docker exec -it football-sim-postgres psql -U football_user -d football_sim

# Reset everything
docker-compose down -v && docker-compose up postgres -d && python manage_db.py init
```

## 💡 Architecture Decisions

### SQLAlchemy Core vs ORM
**Chosen**: SQLAlchemy Core
- **Benefits**: Better performance, explicit SQL control, easier debugging
- **Trade-offs**: More verbose than ORM, manual relationship management

### User-Centric Design
**Approach**: Each user owns their seasons and league data
- **Benefits**: Natural multi-tenancy, data isolation, scalability
- **Implementation**: Foreign keys to users table, DAO filtering by user_id

### JSONB for Statistics
**Usage**: Team stats, player stats, game data stored as JSONB
- **Benefits**: Flexible schema, complex nested data, PostgreSQL optimizations
- **Considerations**: Requires careful indexing for query performance

This database implementation provides a solid foundation for migrating from in-memory storage to persistent, scalable data management. The architecture supports multiple users, complex game simulations, and provides room for future enhancements.