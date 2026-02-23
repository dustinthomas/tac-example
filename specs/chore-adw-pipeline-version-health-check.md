# Chore: Add ADW Pipeline Version to Health Check Output

## Chore Description
Add a version string `ADW Pipeline v2.0` to the health check output so operators can quickly confirm which version of the pipeline is running. The version should appear near the top of the output, right after the "Running ADW System Health Check..." banner.

## Relevant Files

- **`adws/health_check.py`** — The health check script. The `main()` function prints the output; the version string needs to be added here. No other files need changes.

## Step by Step Tasks

### 1. Add ADW_PIPELINE_VERSION constant
- Open `adws/health_check.py`
- After the imports section (after `import re`, before the `from dotenv` import block) add a module-level constant:
  ```python
  ADW_PIPELINE_VERSION = "ADW Pipeline v2.0"
  ```

### 2. Print version in main()
- In `main()`, locate the existing print statement:
  ```python
  print("Running ADW System Health Check...\n")
  ```
- Change it to:
  ```python
  print(f"Running ADW System Health Check... ({ADW_PIPELINE_VERSION})\n")
  ```

### 3. Run Validation Commands

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `uv run adws/health_check.py 2>&1 | head -5` — Confirm "ADW Pipeline v2.0" appears in the first few lines of output
- `cd backend && julia --project=. test/runtests.jl` - Run backend tests with zero regressions
- `cd frontend && npm test` - Run frontend tests with zero regressions
- `cd frontend && npm run typecheck` - TypeScript type checking passes

## Notes
- The change is purely cosmetic — only the printed banner changes, no logic or return values are affected.
- The constant `ADW_PIPELINE_VERSION` should be defined at module level so it can be reused in future scripts if needed.
