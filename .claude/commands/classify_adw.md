# Classify ADW Workflow

Extract the workflow type and ADW ID from the input text. Follow the `Instructions` then `Report`.

## Instructions

- Parse the `Input` text to determine which ADW workflow to run.
- Look for these keywords (case-insensitive):
  - `adw` or `adw_plan_build` → workflow: `plan_build`
  - `adw_sdlc` → workflow: `sdlc`
  - `adw_patch` → workflow: `patch`
  - `adw_test` → workflow: `test`
  - `adw_review` → workflow: `review`
  - `adw_plan_build_test` → workflow: `plan_build_test`
  - `adw_plan_build_review` → workflow: `plan_build_review`
  - `adw_plan_build_test_review` → workflow: `plan_build_test_review`
- If an ADW ID is mentioned (8-character hex string), extract it.
- Default to `plan_build` if just "adw" is specified.

## Input
$ARGUMENTS

## Report

Return ONLY a JSON object (no other text, no markdown fences):

```
{
  "workflow": "plan_build",
  "adw_id": null
}
```

Set `adw_id` to the extracted ID string if found, otherwise `null`.
