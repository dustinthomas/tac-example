# Generate Feature Documentation

Generate documentation for the implemented feature based on the plan file. Follow the `Instructions` then `Report`.

## Instructions

- Read the `Plan File` specified below.
- Read the implementation: `git diff origin/main...HEAD --name-only` to find changed files.
- Create documentation in `app_docs/` directory:
  - Name the file based on the feature (e.g., `app_docs/user-authentication.md`).
  - Create the `app_docs/` directory if it doesn't exist.
- Documentation should include:
  1. **Overview** — What the feature does and why it exists.
  2. **Architecture** — How it fits into the existing system (backend routes, frontend components, database tables).
  3. **Usage** — How to use the feature (API endpoints, UI interactions).
  4. **Configuration** — Any environment variables or settings needed.
  5. **Testing** — How to test the feature manually and what automated tests exist.
- Keep documentation concise and practical — focus on what a developer needs to know.
- Reference actual file paths in the codebase.

## Plan File
$ARGUMENTS

## Report

Return ONLY a JSON object (no other text, no markdown fences):

```
{
  "files_created": ["app_docs/feature-name.md"],
  "summary": "Created documentation for the user authentication feature covering API endpoints, Vue components, and test coverage."
}
```
