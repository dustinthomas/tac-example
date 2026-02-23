# Generate Git Commit

Based on the `Instructions` below, follow the `Run` section to create a git commit with a properly formatted message. Then follow the `Report` section to report the results of your work.

## ADW Context (optional, populated by ADW pipeline)
- **Agent Name:** $ARGUMENTS.agent_name
- **Issue Class:** $ARGUMENTS.issue_class
- **Issue:** $ARGUMENTS.issue

## Instructions

- If ADW context is provided, format commit as: `<agent_name>: <issue_class>: <description>`
- Otherwise, generate a concise commit message in conventional commit format: `<type>: <description>`
- Types: `feat`, `fix`, `chore`, `refactor`, `test`, `docs`
- The `<description>` should be:
  - Present tense (e.g., "add", "fix", "update", not "added", "fixed", "updated")
  - 50 characters or less
  - Descriptive of the actual changes made
  - No period at the end
- Examples:
  - `feat: add user authentication module`
  - `fix: correct login validation error`
  - `chore: update dependencies to latest versions`
- Append `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>` to the commit message body

## Run

1. Run `git diff HEAD` to understand what changes have been made
2. Run `git status` to see all changed and untracked files
3. Stage specific files by name (do NOT use `git add -A` or `git add .`)
4. Run `git commit` with the generated message

## Report

Return ONLY the commit message that was used (no other text)
