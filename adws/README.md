# AI Developer Workflow (ADW) System

ADW automates software development by integrating GitHub issues with Claude Code CLI to classify issues, generate plans, implement solutions, and create pull requests.

**Stack:** Julia/Genie.jl backend + Vue 3/TypeScript frontend + PostgreSQL

## Quick Start

### 1. Set Environment Variables

```bash
export ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export CLAUDE_CODE_PATH="/path/to/claude"  # Optional, defaults to "claude"
export GITHUB_PAT="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # Optional, only if using different account than 'gh auth login'
```

### 2. Install Prerequisites

```bash
# GitHub CLI
sudo pacman -S github-cli    # Manjaro/Arch

# Claude Code CLI
# Follow instructions at https://docs.anthropic.com/en/docs/claude-code

# Python dependency manager (uv)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Authenticate GitHub
gh auth login
```

### 3. Run Health Check

```bash
uv run adws/health_check.py
```

This validates: environment variables, git repo, GitHub CLI auth, Julia (1.12+), PostgreSQL connectivity, Node.js/npm, and Claude Code CLI.

### 4. Run ADW

```bash
cd adws/

# Process a single issue manually
uv run adw_plan_build.py 123

# Run continuous monitoring (polls every 20 seconds)
uv run trigger_cron.py

# Start webhook server (for instant GitHub events)
uv run trigger_webhook.py
```

## Script Usage Guide

### adw_plan_build.py - Process Single Issue

Executes the complete ADW workflow for a specific GitHub issue.

```bash
# Basic usage
uv run adw_plan_build.py 456

# With explicit ADW ID
uv run adw_plan_build.py 456 abc12345

# What it does:
# 1. Fetches issue #456 from GitHub
# 2. Classifies issue type (/chore, /bug, /feature)
# 3. Creates feature branch (feature/, bugfix/, refactor/)
# 4. Generates implementation plan
# 5. Implements the solution
# 6. Creates commits and pull request
```

**Example output:**
```
ADW ID: e5f6g7h8
issue_command: /feature
Working on branch: feature/add-user-authentication
plan_file_path: specs/add-user-authentication-plan.md
Pull request created: https://github.com/owner/repo/pull/789
```

### trigger_cron.py - Automated Monitoring

Continuously monitors GitHub for new issues or "adw" comments.

```bash
# Start monitoring
uv run trigger_cron.py

# Processes issues when:
# - New issue has no comments
# - Latest comment on any issue is exactly "adw"
```

**Production deployment with systemd:**
```bash
# Create service file: /etc/systemd/system/adw-cron.service
sudo systemctl enable adw-cron
sudo systemctl start adw-cron
```

### trigger_webhook.py - GitHub Webhook Server

Receives real-time GitHub events for instant processing. Runs on port 8001 by default (no conflict with Genie.jl on 8000).

```bash
# Start webhook server (default port 8001)
uv run trigger_webhook.py

# Custom port
PORT=3000 uv run trigger_webhook.py

# Configure GitHub webhook:
# URL: https://your-server.com/gh-webhook
# Events: Issues, Issue comments
```

**Endpoints:**
- `POST /gh-webhook` - Receives GitHub events
- `GET /health` - Health check endpoint

### health_check.py - System Health Check

Validates the entire ADW tool chain.

```bash
# Run health check
uv run adws/health_check.py

# Post results to a GitHub issue
uv run adws/health_check.py 123
```

**Checks performed:**
- Environment variables (ANTHROPIC_API_KEY, CLAUDE_CODE_PATH)
- Git repository configuration
- GitHub CLI installation and authentication
- Julia version (1.12+ required)
- PostgreSQL connectivity (fab_ui_dev database)
- Node.js and npm availability
- Claude Code CLI functionality (live test with haiku)

## How ADW Works

1. **Issue Classification**: Analyzes GitHub issue and determines type:
   - `/chore` - Maintenance, documentation, refactoring
   - `/bug` - Bug fixes and corrections
   - `/feature` - New features and enhancements

2. **Branch Creation**: Creates a branch following fab-ui conventions:
   - `feature/` for features
   - `bugfix/` for bugs
   - `refactor/`, `test/`, or `docs/` for chores

3. **Planning**: `sdlc_planner` agent creates implementation plan with:
   - Technical approach
   - Step-by-step tasks
   - File modifications
   - Testing requirements

4. **Implementation**: `sdlc_implementor` agent executes the plan:
   - Analyzes codebase
   - Implements changes
   - Runs tests
   - Ensures quality

5. **Integration**: Creates git commits and pull request:
   - Conventional commit format (`feat:`, `fix:`, `chore:`)
   - Co-authored-by Claude attribution
   - Links to original issue

## Troubleshooting

### Environment Issues
```bash
# Check required variables
env | grep -E "(GITHUB|ANTHROPIC|CLAUDE)"

# Verify GitHub auth
gh auth status

# Test Claude Code
claude --version

# Check Julia
julia --version

# Check PostgreSQL
pg_isready -h localhost

# Check Node.js
node --version && npm --version
```

### Common Errors

**"Claude Code CLI is not installed"**
```bash
which claude  # Check if installed
# Reinstall from https://docs.anthropic.com/en/docs/claude-code
```

**"Julia is not installed" or version too low**
```bash
julia --version
# Install/update from https://julialang.org/downloads/
```

**"PostgreSQL connection failed"**
```bash
sudo systemctl start postgresql
pg_isready -h localhost
psql -h localhost -U fab_ui -d fab_ui_dev -c "SELECT 1;"
```

**"Agent execution failed"**
```bash
# Check agent output
cat agents/*/sdlc_planner/raw_output.jsonl | tail -1 | python3 -m json.tool
```

## Configuration

### ADW Tracking
Each workflow run gets a unique 8-character ID (e.g., `a1b2c3d4`) that appears in:
- Issue comments: `a1b2c3d4_ops: Starting ADW workflow`
- Output files: `agents/a1b2c3d4/sdlc_planner/raw_output.jsonl`
- Git commits and PRs

### Model Selection
Default model is `sonnet` for all agents. Edit `adw_plan_build.py` to use `opus` for complex tasks.

### Output Structure
```
agents/
├── a1b2c3d4/
│   ├── adw_plan_build/
│   │   └── execution.log
│   ├── sdlc_planner/
│   │   ├── raw_output.jsonl
│   │   ├── raw_output.json
│   │   └── prompts/
│   └── sdlc_implementor/
│       ├── raw_output.jsonl
│       ├── raw_output.json
│       └── prompts/
```

## Security Best Practices

- Store tokens as environment variables, never in code
- Use GitHub fine-grained tokens with minimal permissions
- Set up branch protection rules (never commit directly to main)
- Require PR reviews for ADW changes
- Monitor API usage and set billing alerts

## Technical Details

### Core Components
- `utils.py` - ADW ID generation and logging
- `data_types.py` - Pydantic models for type safety
- `github.py` - GitHub API operations via `gh` CLI
- `agent.py` - Claude Code CLI integration
- `adw_plan_build.py` - Main workflow orchestration
- `health_check.py` - System health validation
- `trigger_cron.py` - Poll-based automation
- `trigger_webhook.py` - Event-driven automation

### Branch Naming
```
{type}/{concise-name}
```
Examples: `feature/add-user-auth`, `bugfix/fix-login-error`, `refactor/update-dependencies`

### Commit Format
```
{type}: {description}

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```
