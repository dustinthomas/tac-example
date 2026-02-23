# Conditional Documentation Loading Guide

Determine which documentation files to read based on the task at hand. Follow the `Instructions` then `Report`.

## Instructions

- Read the `Task Description` below.
- Based on the task type, recommend which documentation files to load into context.
- Only recommend files that are directly relevant — minimize context usage.

## Documentation Map

### Backend (Julia/Genie.jl)
- `CLAUDE.md` — Always read first (project conventions, tech stack)
- `ai_docs/genie_reference.md` — Genie.jl routing, middleware, HTTP handling
- `ai_docs/libpq_reference.md` — LibPQ.jl database operations
- `ai_docs/jwts_reference.md` — JWT authentication
- `backend/src/App.jl` — Application entry point and route definitions

### Frontend (Vue 3/TypeScript)
- `CLAUDE.md` — Always read first
- `specs/frontend-architecture.md` — Frontend architecture, component patterns
- `frontend/src/router/index.ts` — Route definitions
- `frontend/src/stores/` — Pinia store patterns

### Database
- `backend/db/migrations/` — Current schema (read all .sql files)
- `CLAUDE.md` — Database access patterns and security rules

### ADW Infrastructure
- `CLAUDE.md` — ADW infrastructure section
- `adws/adw_modules/` — Module source code
- `.claude/commands/` — Available slash commands

### Full Stack Feature
- Read all of the above sections

## Task Description
$ARGUMENTS

## Report
- List the recommended files to read, grouped by category.
- Explain briefly why each file is relevant to the task.
