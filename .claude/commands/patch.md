# Patch Plan

Create a minimal, targeted patch plan in `specs/patch/` to fix a specific issue. Follow the `Instructions` then `Report`.

## Instructions

- IMPORTANT: Patches are surgical fixes — minimal changes, minimal risk.
- Read the `Issue Description` below.
- Research the codebase to identify the exact files and lines that need changing.
- Create the plan in `specs/patch/<issue-slug>.md`.
- Create the `specs/patch/` directory if it doesn't exist.
- The plan should be SHORT and PRECISE — no feature planning, no refactoring.
- Use your reasoning model: THINK HARD about the minimal fix.

## Plan Format

```md
# Patch: <brief description>

## Problem
<1-2 sentences describing the issue>

## Root Cause
<exact file(s) and line(s) where the bug lives>

## Fix
<exact changes needed, as minimal as possible>

## Files to Change
- `path/to/file.ext` — <what to change and why>

## Validation
- `cd frontend && npm test` — zero regressions
- `cd frontend && npm run typecheck` — type checking passes
- `cd backend && julia --project=. test/runtests.jl` — zero regressions
```

## Issue Description
$ARGUMENTS

## Report
- Summarize the patch plan in a concise bullet point list.
- Include the path to the plan file created.
