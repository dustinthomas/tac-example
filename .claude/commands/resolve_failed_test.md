# Resolve Failed Tests

Analyze the test failure output and make minimal fixes to get tests passing. Follow the `Instructions` then `Report`.

## Instructions

- IMPORTANT: Read the `Test Failure Output` carefully. Identify the root cause of each failure.
- IMPORTANT: Make the MINIMAL change needed to fix the failure. Do not refactor surrounding code.
- Fix the actual bug, not the test (unless the test itself is wrong).
- After making fixes, re-run the failing test suite(s) to confirm the fix works.
- If a fix introduces new failures, revert it and try a different approach.
- Do NOT modify tests to make them pass unless the test expectation itself is incorrect.

## Validation

After fixing, run the relevant suite(s):
- `cd frontend && npm run typecheck` — TypeScript type checking
- `cd frontend && npm test` — Frontend tests
- `cd backend && julia --project=. test/runtests.jl` — Backend tests

## Test Failure Output
$ARGUMENTS

## Report
- Summarize the root cause of each failure.
- List every file you changed and why.
- Confirm which suites now pass.
