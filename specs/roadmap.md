# QCI Fab UI — Full Project Roadmap

## Overview

A fabrication management dashboard for QCI's quantum computing facility. Monitors equipment status, manages alerts, tracks operations, and provides admin tools for the fab team.

**Tech Stack:** Vue 3 + TypeScript (no bundler) | Genie.jl (Julia) | PostgreSQL + LibPQ.jl | JWT

---

## Layer 1 — Project Foundation ✅
**Status:** Complete (`7bf0aed`)

- Git repo initialization
- Directory structure (frontend/, backend/, specs/, scripts/, etc.)
- `.claude/settings.json` with permissions
- `.env.sample`, `.gitignore`, `CLAUDE.md`

---

## Layer 2 — Frontend Architecture Spec + VM Setup ✅
**Status:** Complete (`09b4146`)

- No-bundler frontend architecture spec (`specs/frontend-architecture.md`)
- VM setup for AFK agent work (`specs/vm-setup.md`)
- Import map strategy for bare specifiers
- Vendor lib self-hosting approach

---

## Layer 3 — Frontend Scaffolding + Static Serving ✅
**Status:** Complete (`01c7eb5`, browser verified)

- Vue 3 app with Login, Dashboard, Equipment views
- Genie.jl backend serving static files + SPA fallback
- QCI Quantum theme (glassmorphism, dark navy, cyan accents, Raleway)
- Bottom dock navigation bar
- Equipment table with status badges, filters, search
- 29 Vitest unit tests, 3 Playwright E2E specs
- `@vue/devtools-api` stub for import map
- Server keep-alive fix for `Genie.up()`

---

## Layer 4 — Database, Auth & API ✅
**Status:** Complete

### Phase 1: Database
- PostgreSQL schema: `users` and `equipment` tables
- Sequential SQL migrations in `backend/db/migrations/`
- Seed data (admin user + 6 equipment items from mock data)
- Migration runner script (`scripts/migrate.sh`)
- LibPQ.jl connection module (`backend/src/db.jl`)

### Phase 2: Authentication
- JWTs.jl for token creation/validation
- Password hashing (SHA-256 + salt)
- `POST /api/auth/login` endpoint
- Auth middleware (validate Bearer token, attach user context)

### Phase 3: Equipment API
- `GET /api/equipment` — list with filters (status, area, search)
- `GET /api/equipment/:id` — single item
- `PUT /api/equipment/:id` — update status/comment

### Phase 4: Frontend Integration
- API client with auth header injection (`frontend/src/api.ts`)
- Pinia auth store (login, logout, token persistence)
- Pinia equipment store (fetch from API, replace mock data)
- Router navigation guards (require auth)
- Wire LoginView and EquipmentView to stores

### Phase 5: Testing
- Backend: DB connection, auth module, equipment queries, API integration tests
- Frontend: Store tests, router guard tests, updated view tests

---

## Layer 5 — Dashboard & Equipment Management

**Goal:** Make the dashboard a real operational hub and add full equipment CRUD.

### Dashboard Widgets
- Equipment status summary (live counts from API, not hardcoded)
- Recent activity feed (last N status changes)
- Critical alerts panel (equipment marked DOWN or Critical)
- Overall fab health indicator (% operational)

### Equipment CRUD
- `POST /api/equipment` — add new equipment (admin only)
- `DELETE /api/equipment/:id` — remove equipment (admin only)
- Inline status update UI on equipment table (dropdown + comment field)
- Equipment detail view/modal with full history

### API Additions
- `GET /api/dashboard/summary` — aggregated stats for dashboard widgets
- `GET /api/activity/recent` — recent status changes across all equipment
- Role-based access control (admin vs operator permissions on endpoints)

### Frontend
- DashboardView rewrite with real widgets
- Equipment add/edit forms
- Confirmation dialogs for destructive actions
- Loading states and error handling throughout

---

## Layer 6 — Equipment History & Audit Log

**Goal:** Track every status change with full audit trail. Essential for fab compliance.

### Database
- `equipment_history` table: `id, equipment_id, old_status, new_status, comment, changed_by, changed_at`
- Trigger or application-level logging on every `equipment` update
- Index on `equipment_id` + `changed_at` for efficient lookups

### API
- `GET /api/equipment/:id/history` — paginated history for one tool
- `GET /api/audit-log` — global audit log with filters (date range, user, equipment)

### Frontend
- Equipment detail page with history timeline
- Global audit log view (new route: `/audit-log`)
- History entries show: timestamp, who changed, old → new status, comment
- Date range picker for filtering
- Add audit log link to dock nav

---

## Layer 7 — Alerts & Notifications

**Goal:** Proactive monitoring — notify operators when equipment needs attention.

### Database
- `alerts` table: `id, equipment_id, alert_type, severity, message, acknowledged, acknowledged_by, created_at`
- Alert types: `status_change`, `prolonged_down`, `maintenance_due`

### Backend Logic
- Alert generation on status change (auto-create alert when equipment goes DOWN)
- Configurable thresholds (e.g., alert if DOWN > 2 hours)
- Alert acknowledgment endpoint

### API
- `GET /api/alerts` — list alerts (filterable: unacknowledged, severity, equipment)
- `PUT /api/alerts/:id/acknowledge` — mark alert as acknowledged
- `GET /api/alerts/count` — unacknowledged count for badge display

### Frontend
- Alert badge on dock nav icon (unacknowledged count)
- Alerts view (new route: `/alerts`) with alert list and acknowledge buttons
- Alert severity color coding (Critical=red, Warning=orange, Info=cyan)
- Dashboard integration: show critical alerts in dashboard panel

---

## Layer 8 — User Management

**Goal:** Admin interface for managing operator accounts and roles.

### API
- `GET /api/users` — list users (admin only)
- `POST /api/users` — create user (admin only)
- `PUT /api/users/:id` — update user role/password (admin only)
- `DELETE /api/users/:id` — deactivate user (admin only, soft delete)
- `PUT /api/users/:id/password` — change own password (any authenticated user)

### Frontend
- User management view (new route: `/admin/users`, admin only)
- User list table with role badges
- Add/edit user forms
- Password change dialog (accessible from user menu)
- Current user profile display in nav/header area
- Conditional nav items based on role (hide admin pages from operators)

### Backend
- Role-based middleware: `require_role("admin")` for admin-only endpoints
- Soft delete (deactivated flag, not actual deletion)
- Password change validation (require current password)

---

## Layer 9 — Real-Time Updates

**Goal:** Live equipment status updates without manual refresh.

### Approach Decision
Choose one (evaluate during implementation):
- **Option A: Server-Sent Events (SSE)** — simpler, one-directional, sufficient for status broadcasts
- **Option B: WebSocket** — bidirectional, more complex, needed if operators will send commands
- **Option C: Polling** — simplest, every 30s fetch, least infrastructure

### Backend
- SSE/WebSocket endpoint for equipment status stream
- Broadcast status changes to all connected clients on equipment update
- Connection management (track connected clients, handle disconnects)

### Frontend
- Auto-connect on login, reconnect on disconnect
- Update equipment store in real-time from server events
- Update dashboard widgets in real-time
- Visual indicator for live connection status
- Flash/highlight animation on equipment row when status changes

---

## Layer 10 — ADW Tooling & Developer Experience

**Goal:** Agentic Developer Workflow infrastructure for efficient AI-assisted development.
Adapted from tactical-agentic-coding (tac-4) reference implementation.

**Status:** Complete

### Command & Hook Inventory

**Claude Code Commands** (`.claude/commands/`), one command per PR:

| Command | Purpose |
|---------|---------|
| `/prime` | Orient a session — read project tree, CLAUDE.md, roadmap |
| `/start` | Start the development server |
| `/install` | Fresh project setup (deps, migrations, seed, build) |
| `/feature` | Create a feature spec in `specs/` |
| `/bug` | Create a bug fix plan in `specs/` |
| `/chore` | Create a chore plan in `specs/` |
| `/implement` | Read a plan file and implement it |
| `/commit` | Generate a well-formatted commit |
| `/pull-request` | Create a PR via `gh` |
| `/classify-issue` | Classify a GitHub issue as feature/bug/chore |
| `/generate-branch-name` | Create a branch following naming conventions |
| `/find-plan-file` | Locate the most recently created plan file |
| `/tools` | List all available custom commands |

**Claude Code Hooks** (`.claude/hooks/`), Python 3 scripts configured in `.claude/settings.json`:
- `pre_tool_use.py` — Safety guardrails (block dangerous rm, .env access)
- `post_tool_use.py` — Session logging
- `stop.py` — Stop event logging + transcript archival
- `notification.py` — Notification logging
- `utils/constants.py` — Shared session log helpers

---

### Phase 1: Roadmap + `/prime` ✅
**Branch:** `feature/adw-prime` — **PR #5** (merged)

- Update `specs/roadmap.md` Layer 10 section with full command/hook inventory
- Create `.claude/commands/prime.md` (read-only session orientation)
- Remove `.claude/commands/.gitkeep`
- Mark Layer 4 complete in roadmap

---

### Phase 2: Hooks Infrastructure ✅
**Branch:** `feature/adw-hooks` — **PR #7** (merged)

New files:
- `.claude/hooks/utils/__init__.py` — makes utils a Python package
- `.claude/hooks/utils/constants.py` — `LOG_BASE_DIR`, `ensure_session_log_dir()`
- `.claude/hooks/pre_tool_use.py` — block dangerous `rm` commands + `.env` file access, log events
- `.claude/hooks/post_tool_use.py` — log all tool uses to session log
- `.claude/hooks/stop.py` — log stop events, optionally copy transcript to `chat.json`
- `.claude/hooks/notification.py` — log notification events

Update `.claude/settings.json` — add `"hooks"` key with PreToolUse (Bash matcher), PostToolUse, Stop, Notification entries.

Key adaptations from tac-4: no `subagent_stop.py`, no LLM utils, `python3` instead of `uv run --script`, session logs to `logs/<session_id>/`.

---

### Phases 3–14: Commands (one PR each) ✅

Build order follows dependencies — foundational commands first, then workflow commands.

| Phase | Command | Branch | PR | Notes |
|-------|---------|--------|-----|-------|
| 3 | `/tools` | `feature/adw-tools` | #10 | List built-in Claude tools |
| 4 | `/start` | `feature/adw-start` | #11 | Wrap existing `scripts/start.sh` |
| 5 | `/install` | `feature/adw-install` | #12 | npm + Julia Pkg, migrations, seed, vendor download, build |
| 6 | `/feature` | `feature/adw-feature` | #13 | Plan template → `specs/`, validation uses Julia + npm tests |
| 7 | `/bug` | `feature/adw-bug` | #14 | Same template style, fab-ui paths and test commands |
| 8 | `/chore` | `feature/adw-chore` | #15 | Same template style, fab-ui paths and test commands |
| 9 | `/implement` | `feature/adw-implement` | #16 | Read plan from `specs/*.md`, enforce CLAUDE.md rules |
| 10 | `/find-plan-file` | `feature/adw-find-plan` | #17 | Search `specs/` for recently created .md files |
| 11 | `/generate-branch-name` | `feature/adw-branch` | #18 | Format: `feature/`, `bugfix/`, `refactor/`, `test/` (per CLAUDE.md) |
| 12 | `/commit` | `feature/adw-commit` | #19 | Conventional commits, stage specific files (no `git add -A`) |
| 13 | `/pull-request` | `feature/adw-pr` | #20 | `gh pr create`, must run tests first (CLAUDE.md hard rule) |
| 14 | `/classify-issue` | `feature/adw-classify` | #21 | Classify GitHub issues → `/feature`, `/bug`, `/chore` |

#### Key adaptation decisions

**`/install`**: Read `.env.sample` (never `.env`), run `/prime`, `npm install`, `Pkg.instantiate()`, `download-vendor.sh`, `migrate.sh`, `seed_admin.jl`, `npm run build`. Instruct user to fill out `.env`.

**`/feature`, `/bug`, `/chore`**: Output to `specs/`. Relevant files point to `backend/`, `frontend/`, `scripts/`. Validation: `julia test/runtests.jl` + `npm test`. Use `Pkg.add()` (Julia) or `npm install` (frontend), no `uv`.

**`/generate-branch-name`**: Simplified from tac-4 (`feat-123-adw_id-name` → `feature/name`). No ADW ID.

**`/commit`**: Conventional commit format (`type: message`). Types: `feat`, `fix`, `chore`, `refactor`, `test`, `docs`. Stage specific files. Append `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`.

---

### Phase 15: ADW Orchestration Scripts ✅
**Branch:** `feature/adw-orchestration-scripts` — **PR #23** (merged)

Populate `adws/` with Python orchestration scripts adapted from tac-4. These chain the slash commands above to automate the full issue-to-PR workflow.

| Script | Purpose |
|--------|---------|
| `utils.py` | ADW ID generation + logging |
| `data_types.py` | Pydantic models for GitHub API + Claude Code agent |
| `github.py` | GitHub CLI wrappers (fetch issues, post comments, labels) |
| `agent.py` | Claude Code CLI integration (execute slash commands programmatically) |
| `adw_plan_build.py` | Main orchestrator: classify → branch → plan → implement → commit → PR |
| `health_check.py` | Validate full stack: Julia 1.12+, PostgreSQL, Node.js, GitHub CLI, Claude Code |
| `trigger_cron.py` | Poll GitHub every 20s for new issues or "adw" comments |
| `trigger_webhook.py` | FastAPI server (port 8001) for instant GitHub webhook events |

Key adaptations from tac-4: slash command arg signatures match fab-ui commands (`/commit` and `/pull_request` take no args), removed E2B references, added SSH URL handling, fab-ui-specific health checks.

---

### Future Additions

**Scripts:**
- `scripts/reset-db.sh` — drop and recreate DB with migrations + seed
- `scripts/test-all.sh` — run both backend and frontend tests

**AI Docs:**
- `ai_docs/` — curated reference docs for LLM context

---

## Layer 11 — Production Hardening & Deployment

**Goal:** Make the application production-ready.

### Security
- HTTPS (TLS termination — reverse proxy or Genie.jl native)
- Rate limiting on auth endpoints
- CORS configuration
- Input validation on all API endpoints
- SQL injection protection audit (verify all queries parameterized)
- XSS protection (Content-Security-Policy headers)
- Secure cookie/token handling (HttpOnly, Secure, SameSite)

### Performance
- Database connection pooling
- Query optimization (EXPLAIN ANALYZE on common queries)
- Static asset caching headers (vendor JS, CSS)
- Gzip compression for responses

### Reliability
- Structured logging (JSON format for log aggregation)
- Health check endpoint (`GET /api/health`)
- Graceful shutdown handling
- Database backup script
- Error tracking and reporting

### Deployment
- Systemd service file for Genie.jl backend
- Nginx reverse proxy configuration (if needed)
- Environment-specific configuration (dev/staging/prod)
- Deployment checklist document

---

## Layer Dependency Graph

```
Layer 1 (Foundation)
  └─ Layer 2 (Architecture Spec)
       └─ Layer 3 (Frontend Scaffolding)
            └─ Layer 4 (Database, Auth, API)  ✅
                 ├─ Layer 5 (Dashboard & Equipment CRUD)
                 │    └─ Layer 6 (Equipment History & Audit)
                 │         └─ Layer 7 (Alerts & Notifications)
                 ├─ Layer 8 (User Management)
                 └─ Layer 9 (Real-Time Updates)
            └─ Layer 10 (ADW Tooling)  ✅
       └─ Layer 11 (Production Hardening) — after core features complete
```

Layers 5-9 can be reordered based on priority. Layers 10-11 are independent tracks.

---

## Notes

- Each layer = one or more PRs, each PR = one coherent testable change
- TDD approach: write tests alongside or before implementation
- Keep the user learning piece by piece — don't over-automate
- Respect the no-bundler constraint: all frontend changes go through tsc → ES modules
- All database access via LibPQ.jl with parameterized queries, no exceptions
