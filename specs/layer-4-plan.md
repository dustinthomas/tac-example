# Plan: Layer 4 - Database, Auth & API

## Context

Layer 3 (frontend scaffolding + static file serving) is complete and browser-verified. The Vue 3 app renders Login, Dashboard, and Equipment views with hardcoded mock data. This layer adds the backend foundation: PostgreSQL database, JWT authentication, and REST API endpoints to replace the mock data with real server-driven content.

**What exists today:**
- Genie.jl serving static files + SPA fallback routes (`backend/src/App.jl`)
- Vue 3 frontend with Login, Dashboard, Equipment views (hardcoded data)
- 29 Vitest unit tests passing, 3 Playwright E2E specs
- Types defined in `frontend/src/types/index.ts`: `Equipment`, `StatusType`, `CriticalityLevel`, `FabArea`, `StatusSummary`

**What this layer adds:**
- PostgreSQL schema (users + equipment tables)
- Database connection module (LibPQ.jl)
- JWT auth (login endpoint, token validation middleware)
- REST API for equipment CRUD
- Pinia auth store + API integration in frontend
- Router navigation guards (redirect to login if not authenticated)

---

## Tech Stack Reminders

- **Database:** PostgreSQL + LibPQ.jl (direct parameterized SQL, NO ORM)
- **Auth:** JWTs.jl for token creation/validation
- **Password hashing:** Use a Julia package (e.g., `Nettle.jl` for SHA-256 or similar)
- **All SQL:** Hand-written with `$1`, `$2` parameterized queries — NEVER interpolate user input
- **Frontend:** `defineComponent()` + template strings, `.ts` files, no SFCs
- **Imports:** Use `.js` extension in frontend imports (browser ES modules requirement)

---

## Steps

### Phase 1: Database Setup

#### 1.1 PostgreSQL Database Creation
Create the database and user (run manually or via script):
```sql
CREATE DATABASE fab_ui_dev;
CREATE USER fab_ui WITH PASSWORD '<from .env>';
GRANT ALL PRIVILEGES ON DATABASE fab_ui_dev TO fab_ui;
```

#### 1.2 Migration Files
Create `backend/db/migrations/` with sequential SQL files:

**`001_create_users.sql`:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'operator' CHECK (role IN ('admin', 'operator')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Seed admin user (password will be hashed in application)
-- INSERT handled by seed script, not migration
```

**`002_create_equipment.sql`:**
```sql
CREATE TABLE equipment (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    area VARCHAR(50) NOT NULL CHECK (area IN ('Lithography', 'Etching', 'Deposition', 'Metrology')),
    bay VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'DOWN' CHECK (status IN ('UP', 'UP WITH ISSUES', 'MAINTENANCE', 'DOWN')),
    criticality VARCHAR(20) NOT NULL DEFAULT 'Medium' CHECK (criticality IN ('Critical', 'High', 'Medium', 'Low')),
    updated_by VARCHAR(50),
    last_comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**`003_seed_data.sql`:**
Seed the 6 equipment items from the current mock data + a default admin user.

#### 1.3 Migration Runner Script
Create `scripts/migrate.sh` that runs migrations in order via `psql`. Load connection details from `.env`.

#### 1.4 Database Connection Module
Create `backend/src/db.jl`:
- Load connection string from environment variables
- Provide `get_connection()` / `with_connection(f)` helpers
- Use LibPQ.jl `Connection` objects
- Connection pooling is not needed yet (single-server, low-traffic)

### Phase 2: Authentication

#### 2.1 Add Julia Dependencies
```julia
Pkg.add("JWTs")
# For password hashing, check available options (SHA from stdlib, or Nettle.jl)
```

#### 2.2 Auth Module
Create `backend/src/auth.jl`:
- `hash_password(plain::String)::String` — hash with salt
- `verify_password(plain::String, hash::String)::Bool`
- `create_token(user_id::Int, role::String)::String` — JWT with expiry from env
- `validate_token(token::String)::Union{Dict, Nothing}` — decode and validate JWT
- JWT payload: `{ user_id, role, exp }`

#### 2.3 Auth Middleware
Add to `backend/src/App.jl` (or separate middleware file):
- Extract `Authorization: Bearer <token>` header
- Validate token, attach user info to request context
- Return 401 if invalid/expired

#### 2.4 Login API Endpoint
```
POST /api/auth/login
Body: { "username": "...", "password": "..." }
Response: { "token": "...", "user": { "id": 1, "username": "admin", "role": "admin" } }
Error: 401 { "error": "Invalid credentials" }
```

### Phase 3: Equipment API

#### 3.1 Equipment Endpoints
```
GET    /api/equipment          — List all equipment (with optional filters)
GET    /api/equipment/:id      — Get single equipment
PUT    /api/equipment/:id      — Update equipment status/comment
```

Query parameters for list: `?status=UP&area=Lithography&search=beam`

All endpoints require valid JWT (use auth middleware).

#### 3.2 Equipment Module
Create `backend/src/equipment.jl`:
- `list_equipment(conn; status=nothing, area=nothing, search=nothing)` — filtered query
- `get_equipment(conn, id::Int)`
- `update_equipment!(conn, id::Int, status::String, comment::String, updated_by::String)`

All functions use parameterized queries.

### Phase 4: Frontend Integration

#### 4.1 API Client
Create `frontend/src/api.ts`:
- Base URL configuration
- `fetchWithAuth(url, options)` — wrapper that adds JWT header
- Handle 401 responses (redirect to login)

#### 4.2 Auth Store (Pinia)
Create `frontend/src/stores/auth.ts`:
- State: `token`, `user` (id, username, role), `isAuthenticated`
- Actions: `login(username, password)`, `logout()`, `checkAuth()`
- Persist token in `localStorage`

#### 4.3 Equipment Store (Pinia)
Create `frontend/src/stores/equipment.ts`:
- State: `equipment[]`, `loading`, `error`
- Actions: `fetchEquipment(filters?)`, `updateEquipmentStatus(id, status, comment)`
- Replace hardcoded data in EquipmentView with store

#### 4.4 Router Guards
Update `frontend/src/router.ts`:
- `beforeEach` guard: check auth store, redirect to `/login` if not authenticated
- Allow `/login` without auth
- Redirect to `/dashboard` after successful login

#### 4.5 Update LoginView
- Wire form to auth store `login()` action
- Show error messages on failure
- Redirect to `/dashboard` on success

#### 4.6 Update EquipmentView
- Replace hardcoded `equipmentData` with equipment store
- Fetch data from API on mount
- Wire status update UI (if adding inline editing)

### Phase 5: Testing

#### 5.1 Backend Tests
Create `backend/test/` tests for:
- Database connection
- Auth module (hash, verify, token create/validate)
- Equipment queries
- API endpoints (integration tests)

#### 5.2 Frontend Tests
Update/add Vitest tests for:
- Auth store (login, logout, token persistence)
- Equipment store (fetch, update)
- Router guards (redirect behavior)
- LoginView (form submission, error display)
- EquipmentView (loading from store)

---

## Files to Create/Modify

| File | Action | Phase |
|------|--------|-------|
| `backend/db/migrations/001_create_users.sql` | Create | 1 |
| `backend/db/migrations/002_create_equipment.sql` | Create | 1 |
| `backend/db/migrations/003_seed_data.sql` | Create | 1 |
| `scripts/migrate.sh` | Create | 1 |
| `backend/src/db.jl` | Create | 1 |
| `backend/src/auth.jl` | Create | 2 |
| `backend/src/App.jl` | Modify (add API routes + middleware) | 2-3 |
| `backend/Project.toml` | Modify (add JWTs dep) | 2 |
| `frontend/src/api.ts` | Create | 4 |
| `frontend/src/stores/auth.ts` | Create | 4 |
| `frontend/src/stores/equipment.ts` | Create | 4 |
| `frontend/src/router.ts` | Modify (add guards) | 4 |
| `frontend/src/views/LoginView.ts` | Modify (wire to store) | 4 |
| `frontend/src/views/EquipmentView.ts` | Modify (use store) | 4 |
| `backend/test/runtests.jl` | Create/Modify | 5 |
| Frontend test files | Create/Modify | 5 |

---

## Environment Variables Needed

From `.env` (copy `.env.sample` and fill in):
```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=fab_ui_dev
POSTGRES_USER=fab_ui
POSTGRES_PASSWORD=<choose a dev password>
JWT_SECRET=<random string, 32+ chars>
JWT_EXPIRY=3600
BACKEND_PORT=8000
APP_ENV=development
LOG_LEVEL=info
```

---

## Git Workflow

Per CLAUDE.md rules:
- Create branch `feature/database-auth-api`
- Small commits per phase
- Run all tests before PR
- PR to `main` when complete

---

## Verification

After implementation, verify:
1. `psql` can connect and tables exist with seed data
2. `POST /api/auth/login` returns JWT with valid credentials
3. `GET /api/equipment` returns equipment list (requires JWT)
4. Frontend login form authenticates and redirects to dashboard
5. Equipment page loads data from API
6. Unauthenticated access redirects to login
7. All existing tests still pass + new tests pass
