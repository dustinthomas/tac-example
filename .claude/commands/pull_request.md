# Create Pull Request

Based on the `Instructions` below, follow the `Run` section to create a pull request. Then follow the `Report` section to report the results of your work.

## Instructions

- IMPORTANT: Run tests before creating the PR (CLAUDE.md hard rule).
- Generate a PR title in conventional commit format: `<type>: <short description>`
- The PR body should include:
  - A `## Summary` section with bullet points of key changes
  - A `## Test plan` section with a checklist of what to verify
  - Link to the plan file if one exists in `specs/`
- Examples of PR titles:
  - `feat: Add user authentication`
  - `fix: Correct login validation error`
  - `chore: Update dependencies`

## Run

1. Run `cd frontend && npm test` to run frontend tests
2. Run `cd frontend && npm run typecheck` to verify TypeScript
3. Run `git diff origin/main...HEAD --stat` to see a summary of changed files
4. Run `git log origin/main..HEAD --oneline` to see the commits included
5. Run `git push -u origin HEAD` to push the branch
6. Run `gh pr create --title "<pr_title>" --body "<pr_body>" --base main` to create the PR
7. Capture the PR URL from the output

## Report

Return ONLY the PR URL that was created (no other text)
