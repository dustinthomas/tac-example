# Code Review Against Spec

Follow the `Instructions` below to **review work done against a spec/plan file** to ensure implemented features match requirements. Use the spec file to understand the requirements and the git diff to understand the changes made. Capture screenshots of critical functionality paths using Playwright. If there are issues, report them; if not, report success.

## Variables

adw_id: $1
spec_file: $2
agent_name: $3 if provided, otherwise use 'review_agent'
review_image_dir: `/home/agent/Git/Projects/fab-ui_2-0/agents/<adw_id>/<agent_name>/review_img/`

## Instructions

- Check current git branch using `git branch` to understand context
- Run `git diff origin/main` to see all changes made in current branch. Continue even if there are no changes related to the spec file.
- Read the spec file (`$2`) to understand requirements
- Read every file changed since branching from main: `git diff origin/main...HEAD --name-only`
- For each changed file, verify:
  1. **Correctness:** Does the implementation match the spec's requirements?
  2. **Completeness:** Are all spec steps implemented?
  3. **Security:** No SQL injection, XSS, command injection, or credential leaks (OWASP top 10).
  4. **Style:** Follows CLAUDE.md coding conventions (Julia: snake_case, 4-space indent; TS: camelCase, 2-space indent).
  5. **Tests:** Are there adequate tests for new functionality?
- IMPORTANT: If the work can be validated by UI validation then (if not, skip the screenshot section):
  - IMPORTANT: We're not testing. We know the functionality works. We're reviewing the implementation against the spec to make sure it matches what was requested.
  - IMPORTANT: Take screenshots along the way to showcase the new functionality and any issues you find
    - Use Playwright to navigate to the running application and capture screenshots of critical paths based on the spec
    - Compare implemented UI changes with spec requirements to verify correctness
    - Do not take screenshots of the entire process, only the critical points
    - IMPORTANT: Aim for `1-5` screenshots to showcase that the new functionality works as specified
    - If there is a review issue, take a screenshot of the issue and add it to the `review_issues` array. Describe the issue, resolution, and severity.
    - Number screenshots in order: `01_<descriptive_name>.png`, `02_<descriptive_name>.png`, etc.
    - IMPORTANT: Be absolutely sure to take a screenshot of the critical point of the new functionality
    - IMPORTANT: Store all screenshots in the `review_image_dir` using full absolute paths
    - Use descriptive filenames that indicate what part of the change is being verified
  - Playwright screenshot example:
    ```bash
    npx playwright screenshot --wait-for-timeout=2000 "http://localhost:8000" /absolute/path/to/screenshot.png
    ```
    - Use `--wait-for-timeout=2000` to allow the page to fully render
    - For pages behind auth, use a Playwright script to log in first, then capture
- IMPORTANT: Issue Severity Guidelines
  - Think hard about the impact of the issue on the feature and the user
  - Guidelines:
    - `skippable` — Non-blocker but still a problem worth noting
    - `tech_debt` — Non-blocker but will create technical debt that should be addressed later
    - `blocker` — Must fix before merge. Harms user experience or functionality does not work as expected.
- Ultra think as you work through the review process. Focus on the critical functionality paths and the user experience. Don't report issues if they are not critical to the feature.

## Setup

IMPORTANT: Read and **Execute** `.claude/commands/prepare_app.md` now to prepare the application for the review.

## Report

- IMPORTANT: Return results exclusively as a JSON object based on the `Output Structure` section below.
- IMPORTANT: Do not include any additional text, explanations, or markdown formatting
- We'll immediately run JSON.parse() on the output, so make sure it's valid JSON
- `success` should be `true` if there are NO BLOCKING issues (implementation matches spec for critical functionality)
- `success` should be `false` ONLY if there are BLOCKING issues that prevent the work from being released
- `review_issues` can contain issues of any severity (skippable, tech_debt, or blocker)
- `screenshots` should ALWAYS contain paths to screenshots showcasing the new functionality, regardless of success status. Use full absolute paths.

### Output Structure

```json
{
    "success": "boolean - true if NO blockers, false if any blockers",
    "review_summary": "string - 2-4 sentences describing what was built and whether it matches the spec. Written as if reporting during a standup meeting.",
    "review_issues": [
        {
            "review_issue_number": 1,
            "file": "path/to/file.ts",
            "line": 42,
            "screenshot_path": "/absolute/path/to/screenshot_showing_issue.png",
            "issue_description": "string - description of the issue",
            "issue_resolution": "string - description of the resolution",
            "issue_severity": "skippable | tech_debt | blocker"
        }
    ],
    "screenshots": [
        "/absolute/path/to/01_feature_overview.png",
        "/absolute/path/to/02_critical_path.png"
    ]
}
```
