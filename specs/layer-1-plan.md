# Plan: Layer 1 - Project Foundation for fab-ui-2-0

## Context

Setting up the foundational environment for a greenfield project called **fab-ui-2-0**, adapting the "Agentic Developer Workflow" (ADW) pattern from the tac-4 reference project. This is Layer 1 only - the bare minimum to get git, Claude Code config, and project structure in place. Later layers will add ADW scripts, hooks, commands, and actual application code.

**Tech Stack:**
- Frontend: Vue 3 + TypeScript + Vite
- Backend: Genie.jl (Julia) - no SearchLight ORM
- Database: PostgreSQL + LibPQ.jl (direct SQL)
- Auth: JWT via JWTs.jl
- Dev environment: VM on local machine

**Current state of `/home/dustin/Git/Projects/fab-ui_2-0`:**
- `.claude/settings.local.json` - local permissions (lsof, ss, web, julia, npm, psql, gh)
- `index.html` - 45KB QCI Fab UI design reference (static HTML with Quantum theme)
- No git repo initialized

---

## Steps

### 1. Initialize git repo
```bash
cd /home/dustin/Git/Projects/fab-ui_2-0
git init
```

### 2. Create directory structure
```
fab-ui_2-0/
├── .claude/
│   ├── settings.json      # CREATE - project permissions (committed)
│   ├── settings.local.json # EXISTS - local overrides (gitignored)
│   └── commands/           # CREATE - empty, for later layers
├── frontend/               # CREATE - Vue + TS + Vite (empty for now)
├── backend/                # CREATE - Genie.jl API (empty for now)
├── scripts/                # CREATE - utility shell scripts
├── specs/                  # CREATE - feature specifications
├── ai_docs/                # CREATE - curated LLM reference docs
├── adws/                   # CREATE - AI Developer Workflow scripts
├── agents/                 # CREATE - agent output (gitignored)
├── logs/                   # CREATE - session logs (gitignored)
├── .gitignore              # CREATE
├── .env.sample             # CREATE
├── CLAUDE.md               # CREATE
└── index.html              # EXISTS - preserve
```

Each empty directory gets a `.gitkeep` file so git tracks it.

### 3. Create `.gitignore`
Covers: environment files, Julia artifacts (*.jl.cov, *.jl.mem), Node (node_modules/, dist/), IDE files, OS files, logs/, agents/, `.claude/settings.local.json`, SSL/secrets.

**Key decision:** `Manifest.toml` is NOT gitignored (kept for reproducibility).

### 4. Create `.claude/settings.json`
Permissions only (no hooks - those come in later layers):

**Allow list** (adapted from tac-4, replacing Python/uv with Julia):
- `julia:*`, `npm:*`, `npx:*`, `node:*` - language tooling
- `git:*`, `gh:*` - version control
- `psql:*` - database
- `mkdir:*`, `mv:*`, `cp:*`, `chmod:*`, `touch:*` - filesystem
- `find:*`, `grep:*`, `ls:*`, `cat:*`, `head:*`, `tail:*` - read-only
- `Write` - Claude Code file writes

**Deny list:**
- `git push --force`, `git push -f` - protect remote history
- `rm -rf /`, `rm -rf ~`, `rm -rf .` - prevent catastrophic deletions

**Note:** `rm` is NOT in the allow list, so Claude gets prompted for any rm command. Only catastrophic variants are explicitly denied.

### 5. Create `.env.sample`
Template with empty values for:
- PostgreSQL: `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- JWT: `JWT_SECRET`, `JWT_EXPIRY`
- App: `BACKEND_PORT` (8000), `FRONTEND_PORT` (5173), `APP_ENV`, `LOG_LEVEL`
- ADW/Claude: `ANTHROPIC_API_KEY`, `CLAUDE_CODE_PATH`, `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR`
- GitHub: `GITHUB_PAT` (optional)

### 6. Create `CLAUDE.md`
Project rulebook covering:
- Project overview and tech stack
- Hard rules (no direct commits to main, no secrets, run tests before PR)
- Coding style (Julia: snake_case/4-space, TS/Vue: camelCase/2-space)
- Tech stack details (Genie.jl + LibPQ.jl direct SQL, Vue 3 Composition API)
- Development commands (julia, npm, psql, git)
- Project structure reference
- Database access pattern (LibPQ.jl parameterized queries)
- JWT auth pattern
- QCI branding/theme colors (from existing index.html)
- ADW infrastructure status (Layer 1 - foundation only)
- Lessons learned template

### 7. Initial git commit
Stage files individually (not `git add .`), then commit:
```
Layer 1: Initialize project foundation

- Set up directory structure for Vue/TypeScript + Genie.jl + PostgreSQL stack
- Configure .claude/settings.json with Julia/Node tooling permissions
- Add .gitignore covering Julia, Node/Vue, PostgreSQL, ADW artifacts
- Add .env.sample with database, JWT, and ADW configuration
- Add CLAUDE.md project context document
- Preserve index.html design reference from QCI Fab UI
```

---

## Files to create/modify

| File | Action |
|------|--------|
| `.gitignore` | Create |
| `.claude/settings.json` | Create |
| `.env.sample` | Create |
| `CLAUDE.md` | Create |
| 9 directories with `.gitkeep` | Create |

**Reference files (tac-4):**
- `.claude/settings.json` - pattern for permissions
- `.env.sample` - pattern for env vars
- `.gitignore` - pattern for ignores

---

## What this does NOT include (deferred)

| Item | Layer |
|------|-------|
| `.claude/hooks/` (PreToolUse, PostToolUse, etc.) | Layer 2 |
| `.claude/commands/` slash commands | Layer 2 |
| `adws/` orchestration scripts | Layer 2 |
| `ai_docs/` content | Layer 2 |
| Vue + Vite scaffolding | Layer 3 |
| Genie.jl scaffolding | Layer 3 |
| PostgreSQL setup + migrations | Layer 3 |
| VM setup | Separate discussion |
| Docker / CI/CD | Layer 4+ |

---

## Verification

After implementation, verify:
1. `git status` shows clean working tree
2. `git log --oneline` shows the initial commit
3. `.claude/settings.local.json` is NOT tracked
4. `agents/` and `logs/` directories exist but only `.gitkeep` is tracked
5. Running `claude` from project root picks up CLAUDE.md context
6. No `.env` file is committed (only `.env.sample`)
