# Run Validation Suite

Run the full validation suite and return structured results. Follow the `Instructions` then `Report` the results.

## Instructions

- Run each test suite below in order.
- Capture stdout and stderr from each command.
- Do NOT stop on first failure — run all suites regardless.
- After all suites complete, compile the results into the JSON format specified in `Report`.

## Test Suites

### 1. Frontend TypeCheck
```bash
cd frontend && npm run typecheck
```

### 2. Frontend Tests
```bash
cd frontend && npm test
```

### 3. Backend Tests
```bash
cd backend && julia --project=. test/runtests.jl
```

## Report

Return ONLY a JSON array (no other text, no markdown fences) with one object per suite:

```
[
  {"suite": "frontend_typecheck", "passed": true, "output": "<stdout>", "error": null},
  {"suite": "frontend_test", "passed": true, "output": "<stdout>", "error": null},
  {"suite": "backend_test", "passed": true, "output": "<stdout>", "error": null}
]
```

Set `passed` to `false` and populate `error` with stderr if a suite fails (non-zero exit code).
