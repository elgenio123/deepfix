# DeepFix API - FastAPI Backend

This is the FastAPI backend server for the DeepFix portal.

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your database URL and other settings
   ```

3. **Set up database:**
   - Make sure PostgreSQL is running
   - Update `DATABASE_URL` in `.env`
   - Run migrations:
     ```bash
     alembic upgrade head
     ```

## Development

Run the FastAPI server:
```bash
npm run dev:api
# or
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 5000
```

The API will be available at `http://localhost:5000`

API documentation (Swagger UI) will be available at:
- `http://localhost:5000/docs`
- `http://localhost:5000/redoc` (alternative docs)

## Project Structure

```
api/
├── main.py              # FastAPI app entry point
├── database.py          # Database configuration
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── utils.py             # Utility functions (auth, hashing)
├── dependencies.py      # FastAPI dependencies
├── routes/
│   ├── auth.py          # Authentication routes
│   ├── api_keys.py      # API key management
│   └── users.py         # User management
└── migrations/          # Alembic database migrations
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/signup` - Sign up
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

### API Keys
- `GET /api/api-keys/` - List API keys
- `POST /api/api-keys/` - Create API key
- `GET /api/api-keys/{key_id}` - Get API key
- `DELETE /api/api-keys/{key_id}` - Revoke API key

### Users
- `GET /api/users/` - List users (admin)
- `GET /api/users/{user_id}` - Get user

## TODO: Implementation Status

All endpoints currently return `501 Not Implemented` with placeholder code. You need to:

1. **Implement password hashing** (`api/utils.py`)
   - Install bcrypt: `pip install passlib[bcrypt]`
   - Uncomment and implement `hash_password()` and `verify_password()`

2. **Implement JWT tokens** (`api/utils.py`)
   - Install python-jose: `pip install python-jose[cryptography]`
   - Uncomment and implement `create_access_token()` and `verify_token()`

3. **Implement authentication routes** (`api/routes/auth.py`)
   - Uncomment and implement login, signup, logout logic

4. **Implement API key routes** (`api/routes/api_keys.py`)
   - Uncomment and implement API key generation and management

5. **Set up database migrations**
   ```bash
   alembic init migrations
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

6. **Update CORS settings** in `api/main.py` with your frontend URLs

7. **Set environment variables** in `.env`:
   - `DATABASE_URL`
   - `SECRET_KEY` (for JWT)
   - Other settings as needed

## Database Models

- **User**: id, username, email, password (hashed), name, created_at, updated_at, is_active
- **APIKey**: id, user_id, key, name, last_used, created_at, is_active

## Notes

- Frontend (React) remains unchanged and should work with the FastAPI backend once endpoints are implemented
- Make sure to update the frontend API calls to match the FastAPI endpoint structure

