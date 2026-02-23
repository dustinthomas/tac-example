# CLAUDE.md

This is the rulebook for Claude Code sessions working in this repository.

## Project Overview

**fab-ui-2-0** is a web application for quantum computing fabrication management at QCI. It provides a dashboard for monitoring equipment status, managing alerts, and tracking fab operations.

- **Frontend:** Vue 3 (Composition API) + TypeScript (no bundler — tsc transpiles .ts → .js, served as ES modules)
- **Backend:** Genie.jl (Julia web framework)
- **Database:** PostgreSQL with LibPQ.jl (direct SQL, no ORM)
- **Auth:** JWT via JWTs.jl
- **Platform:** Manjaro Linux VM

## Hard Rules

- Never commit directly to `main`; always use feature branches
  - Branch naming: `feature/NAME`, `bugfix/NAME`, `refactor/NAME`, `test/NAME`
- Never commit .env files, secrets, API keys, or credentials
- Never commit node_modules/ or tsc build output (`backend/public/js/app/`)
- Vendor ES modules in `backend/public/js/vendor/` ARE committed (pinned, self-hosted)
- Always run tests before proposing a PR
- Keep dependencies minimal
- Prioritize simplicity over cleverness
- Keep work units small: each PR = one coherent, testable change

## Coding Style

### Julia (Backend)

**Style & naming:**
- 4-space indentation, lines under 100 characters
- `snake_case` for functions and variables (project convention; official Julia prefers squashed lowercase like `haskey`)
- `PascalCase` for modules and types/structs
- Mutating functions end with `!` (e.g., `push!`, `update_status!`)
- Don't parenthesize `if`/`while` conditions — `if a == b` not `if (a == b)`

**Function design:**
- Break code into small functions — top-level code runs slower and is harder to test
- Functions take arguments instead of operating on global variables
- Mark globals as `const` with type annotations when unavoidable
- Pass functions directly — `map(f, a)` not `map(x -> f(x), a)`
- Prefer avoiding errors over catching them — minimize `try`/`catch`

**Type system & performance:**
- Use concrete types for struct fields (`Int`, `String`) not abstract types (`Number`, `Any`)
- Parameterize structs when field type varies: `struct Wrapper{T} data::T end`
- Write generic function signatures — use `AbstractString` instead of `String` for inputs
- Don't change a variable's type mid-function (type stability)
- Use `@code_warntype` to catch type instability in hot paths

**Security:**
- Sanitize all external input at the Genie.jl route/middleware layer before processing
- Never interpolate user input into shell commands (`run()`) — use argument vectors
- Never use `unsafe_` functions without explicit justification
- Use `RandomDevice()` for cryptographic randomness, never `rand()`

### TypeScript / Vue (Frontend)
- 2-space indentation
- `camelCase` for functions and variables
- `PascalCase` for components and types
- **No SFCs (.vue files).** Components use `defineComponent()` with template strings in `.ts` files
- Composition API only (via `setup()` function inside `defineComponent()`)
- Relative imports must use `.js` extension (e.g., `import App from './App.js'`) — required by browser ES modules

## Tech Stack Details

### Backend: Genie.jl + LibPQ.jl
- **No ORM.** This project uses LibPQ.jl for direct PostgreSQL access.
- All SQL is hand-written with parameterized queries.
- Julia 1.12+, Genie.jl for routing/middleware/HTTP.
- JWTs.jl for JWT token creation and validation.

### Frontend: Vue 3 + TypeScript (No Bundler)
- **Architecture:** Agent writes `.ts` → `tsc` transpiles to `.js` → Genie.jl serves `.js` as ES modules
- **No bundler.** No Vite, Webpack, or esbuild in the pipeline. Node/npm is a dev-only dependency (agent VM only, not production).
- **Vue browser build:** Uses `vue.esm-browser.js` (full build with runtime template compiler)
- **Import maps:** `backend/public/index.html` contains a `<script type="importmap">` that maps bare specifiers (e.g., `'vue'`) to self-hosted vendor files in `/js/vendor/`
- **Vendor libs:** Vue 3, Pinia, Vue Router ESM browser builds are downloaded once and committed to `backend/public/js/vendor/`
- State management: Pinia
- Routing: Vue Router
- Styling: CSS with QCI Quantum theme (glassmorphism, Raleway font)
- See `specs/frontend-architecture.md` for full details

### Database: PostgreSQL
- Direct SQL via LibPQ.jl
- Migrations managed as sequential .sql files in `backend/db/migrations/`

## Development Commands

```bash
# Julia backend
cd backend && julia --project=. -e 'using Pkg; Pkg.instantiate()'  # Install deps
cd backend && julia --project=. src/App.jl                          # Start server

# Julia package management
cd backend && julia --project=. -e 'using Pkg; Pkg.add("PackageName")'

# Frontend (dev-only — Node is NOT a production dependency)
cd frontend && npm install          # Install deps (typescript + type declarations)
cd frontend && npm run typecheck    # Type-check only (tsc --noEmit)
cd frontend && npm run build        # Transpile .ts → backend/public/js/app/*.js
cd frontend && npm run watch        # Watch mode (tsc --watch)

# Database
psql -h localhost -U fab_ui -d fab_ui_dev

# Tests
cd backend && julia --project=. test/runtests.jl
cd frontend && npm test

# Git workflow
git checkout -b feature/my-feature
git add <files> && git commit
gh pr create --fill
```

## Project Structure

```
fab-ui_2-0/
├── CLAUDE.md              # This file
├── .claude/
│   ├── settings.json      # Claude Code permissions (committed)
│   └── commands/          # Custom slash commands
├── .env.sample            # Environment variable template
├── .gitignore
├── index.html             # Static design reference (QCI theme)
├── frontend/              # Vue 3 + TypeScript source (.ts files, dev tooling)
│   ├── src/               # .ts source files (components, router, stores)
│   ├── tsconfig.json      # TypeScript config (paths, outDir → backend/public/js/app)
│   └── package.json       # Dev-only deps: typescript, @types/*, vue type declarations
├── backend/               # Julia / Genie.jl API
│   └── public/            # Static assets served by Genie.jl
│       ├── index.html     # Entry point with import map
│       ├── css/            # QCI Quantum theme stylesheets
│       └── js/
│           ├── app/        # tsc output (.js files, gitignored)
│           └── vendor/     # Self-hosted Vue/Pinia/Router ES modules (committed)
├── scripts/               # Utility shell scripts
├── specs/                 # Feature specifications
├── ai_docs/               # Curated LLM reference docs
├── adws/                  # AI Developer Workflow scripts
├── agents/                # Agent execution output (gitignored)
└── logs/                  # Session logs (gitignored)
```

## Database Access Pattern

LibPQ.jl with parameterized queries:

```julia
using LibPQ

function get_equipment(conn::LibPQ.Connection, id::Int)
    result = execute(conn, "SELECT * FROM equipment WHERE id = \$1", [id])
    # Process result...
end
```

Key principles:
- Always use parameterized queries (`$1`, `$2`, etc.)
- Never string-interpolate user input into SQL
- Wrap multi-step operations in transactions
- Close/return connections properly

### Database Security

**Authentication & access control:**
- Never use `trust` or plain MD5 auth — use SCRAM-SHA-256 in `pg_hba.conf`
- Restrict `listen_addresses` and `pg_hba.conf` to application server IPs only
- Never connect as the `postgres` superuser from the application — use a dedicated least-privilege role
- Credentials come from environment variables (`.env`), never hardcoded

**Encryption:**
- Require SSL/TLS for all connections (`sslmode=require` in connection string, `ssl = on` in `postgresql.conf`)
- Use `sslmode=verify-full` with CA-signed certs in production
- Use filesystem-level encryption (LUKS) or `pgcrypto` for sensitive data at rest
- Hash passwords with a salt — never store plaintext

**Role-based access (RBAC):**
- Create separate DB roles for read-only vs read-write operations
- Revoke default public schema access (`REVOKE ALL ON SCHEMA public FROM public`)
- Use Row-Level Security (RLS) if multi-tenant access is needed
- Grant only the minimum permissions each role requires

**Attack prevention:**
- Use `fail2ban` or equivalent to block brute-force login attempts on port 5432
- Enable `log_connections = on` in Postgres config but never log sensitive data (passwords, tokens)

**Maintenance:**
- Keep PostgreSQL, Julia packages, and OS dependencies patched
- Encrypt database backups and test restores periodically
- Enable `pg_audit` extension for change tracking in production
- Monitor connection pools to prevent leaks and resource exhaustion

## JWT Auth Pattern

- Access tokens in `Authorization: Bearer <token>` header
- Tokens contain: user_id, role, expiry
- Middleware validates token on protected routes
- Roles: `admin`, `operator`

## QCI Branding

- **Dark Navy:** `#1E204B`
- **Light Navy:** `#222354`
- **Cyan Accent:** `#00BCD4`
- **Light Grey:** `#F4F5F9`
- **White:** `#FFFFFF`
- **Font:** Raleway (Google Fonts)
- Status: UP=#2ecc71, ISSUES=#f39c12, MAINTENANCE=#e67e22, DOWN=#e74c3c

## ADW Infrastructure

This project uses an Agentic Developer Workflow (ADW) approach:
- `adws/` - agent orchestration scripts
- `specs/` - feature specifications
- `ai_docs/` - curated documentation for LLM context
- `agents/` - agent execution output (gitignored)
- `logs/` - session logs (gitignored)
- `.claude/commands/` - custom slash commands

**Status:** Layer 10 complete. All commands and hooks are implemented.

## Lessons Learned

### 2026-02-16 - @vue/devtools-api missing from import map
**What happened:** Pinia and Vue Router ESM browser builds both `import { setupDevtoolsPlugin } from '@vue/devtools-api'`. This bare specifier wasn't in the import map, so the browser threw `TypeError: Failed to resolve module specifier` and the Vue app never mounted — only the CSS background gradient rendered.
**Rule:** When adding vendor ESM browser builds, check their imports for transitive bare specifiers (e.g. `@vue/devtools-api`) and add stubs or real modules to the import map. A no-op stub works fine for devtools in production.

### 2026-02-16 - Genie.jl up() returns immediately
**What happened:** `Genie.up()` starts the HTTP server in a background task and returns immediately. When used as `julia -e 'include("App.jl"); App.main()'`, the process exits as soon as `main()` returns, killing the server. The `start.sh` health check (`kill -0 $PID`) then reports "Backend failed to start!" even though the server briefly ran.
**Rule:** Always block the main thread after `up()` with a `while true; sleep(1); end` loop (wrapped in `try/catch InterruptException` for clean Ctrl+C shutdown). This keeps the process alive for the server's background task.

### Template
```
### [DATE] - [Brief description]
**What happened:** [describe]
**Rule:** [new rule]
```
