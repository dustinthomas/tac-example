# Chore: Add main() Entry Point Comment to App.jl

## Chore Description
Add a brief inline doc comment above the `main()` function in `backend/src/App.jl` explaining what the function does. This is a documentation improvement to make the entry point self-describing for new developers and for ADW pipeline validation.

## Relevant Files

- `backend/src/App.jl` — Contains the `main()` function at line 243. This is the only file that needs to be modified. The comment will be added directly above the `function main()` declaration.

## Step by Step Tasks

### Step 1: Add inline doc comment to main()

- Open `backend/src/App.jl`
- Insert a Julia docstring comment immediately above `function main()` (currently line 243), following the existing pattern used for other functions in the file (e.g., `load_env!` at line 26 and `json_error` at line 38)
- The comment should concisely describe what `main()` does: loads environment variables, configures and starts the Genie.jl HTTP server, and blocks the main thread to keep the process alive
- Use Julia triple-quoted docstring style: `"""..."""`

The resulting code should look like:

```julia
"""Entry point: loads environment config, starts the Genie.jl HTTP server, and blocks the main thread to keep the process alive."""
function main()
    load_env!()
    ...
```

### Step 2: Run validation commands

- Run all validation commands listed below to confirm zero regressions.

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `cd backend && julia --project=. test/runtests.jl` - Run backend tests with zero regressions
- `cd frontend && npm test` - Run frontend tests with zero regressions
- `cd frontend && npm run typecheck` - TypeScript type checking passes

## Notes
- The existing functions in App.jl already use `"""..."""` docstrings (see `load_env!`, `json_error`, `authenticate_request`). Follow the same one-line style for consistency.
- No new packages, migrations, or files are needed — this is a pure documentation change.
