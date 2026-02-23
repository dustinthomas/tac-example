# Feature: Indicator Badge Label Color Match

## Metadata
issue_number: `bage`
adw_id: `workd`
issue_json: `color`

## Feature Description
The Equipment Status page displays four status summary chips in the header (Operational, With Issues, Maintenance, Down). Each chip shows a colored number count (e.g., green for UP, yellow for issues, orange for maintenance, red for down) and a text label below it. Currently the label text is rendered in a muted white/grey color regardless of chip type. This feature updates the label text color to match the color of the number count for each chip type, making the visual design more cohesive and immediately communicating status through color.

## User Story
As a fab operator
I want the status chip label text to match the color of the indicator number
So that the status badges are visually consistent and communicate status at a glance

## Problem Statement
The status summary chips in the Equipment Status header use distinct colors for the numeric count (green=UP, yellow=issues, orange=maintenance, red=down) but the label text below each count renders in a uniform muted white. This visual inconsistency makes the badges feel disconnected — the color meaning of the count is not reinforced by the label.

## Solution Statement
Add per-status CSS rules to the `.chip-label` element within each status chip variant (`.status-chip.up`, `.status-chip.issues`, `.status-chip.maintenance`, `.status-chip.down`) so the label inherits the same status color as the count. Retain reduced opacity on the label so it appears slightly softer than the count while still color-matched.

## Relevant Files

- `backend/public/css/quantum-theme.css` — Contains all `.status-chip` and `.chip-label` styles. This is where the CSS change is made (lines ~548–566).
- `frontend/src/views/EquipmentView.ts` — Renders the status chips template with `.status-chip.up/issues/maintenance/down` classes and `.chip-label` span. No change needed but must verify class names match.
- `frontend/src/__tests__/views/EquipmentView.spec.ts` — Existing tests for EquipmentView. A new test asserting chip label text content (and optionally CSS class presence) should be added.

## Implementation Plan
### Phase 1: Foundation
Understand the current CSS structure for status chips and confirm the exact class selectors used for each status variant and their label elements.

### Phase 2: Core Implementation
Add four CSS rules in `quantum-theme.css` — one per status variant — that set the `.chip-label` color to match the corresponding status CSS variable:
- `.status-chip.up .chip-label { color: var(--status-up); }`
- `.status-chip.issues .chip-label { color: var(--status-issues); }`
- `.status-chip.maintenance .chip-label { color: var(--status-maintenance); }`
- `.status-chip.down .chip-label { color: var(--status-down); }`

The existing `opacity: 0.7` on `.chip-label` remains so labels appear slightly softer than the bold count number.

### Phase 3: Integration
Verify visually and through existing tests that no regressions occur. Add a targeted test to confirm chip labels render with correct text per status type.

## Step by Step Tasks

### Step 1: Read the current CSS
- Open `backend/public/css/quantum-theme.css` and confirm lines ~548–566 containing `.chip-label` and `.chip-count` rules.
- Confirm the CSS variable names used: `--status-up`, `--status-issues`, `--status-maintenance`, `--status-down`.

### Step 2: Add chip-label color rules to CSS
- In `backend/public/css/quantum-theme.css`, immediately after the existing `.chip-count` color rules (after line 566), add four new rules:
  ```css
  .status-chip.up .chip-label { color: var(--status-up); }
  .status-chip.issues .chip-label { color: var(--status-issues); }
  .status-chip.maintenance .chip-label { color: var(--status-maintenance); }
  .status-chip.down .chip-label { color: var(--status-down); }
  ```

### Step 3: Add a test to EquipmentView spec
- In `frontend/src/__tests__/views/EquipmentView.spec.ts`, add a new `it` block that:
  - Mounts the component and flushes promises
  - Finds `.chip-label` elements and verifies they render with correct label text: `['Operational', 'With Issues', 'Maintenance', 'Down']`
  - This confirms the template structure is correct and labels are rendered (CSS color cannot be checked in jsdom but label presence and text can be verified)

### Step 4: Run validation commands
- Run all validation commands listed below to confirm zero regressions.

## Testing Strategy
### Unit Tests
- Verify all four `.chip-label` elements render with correct text content in EquipmentView.
- Verify chip class names (`up`, `issues`, `maintenance`, `down`) are applied correctly.

### Integration Tests
- Visual inspection of the Equipment Status page in browser to confirm label colors match count colors.

### Edge Cases
- All four status types present: all four labels should be colored.
- Zero count for a status: chip still renders with color-matched label.

## Acceptance Criteria
- `.status-chip.up .chip-label` text is green (`var(--status-up)` = `#2ecc71`)
- `.status-chip.issues .chip-label` text is yellow (`var(--status-issues)`)
- `.status-chip.maintenance .chip-label` text is orange (`var(--status-maintenance)`)
- `.status-chip.down .chip-label` text is red (`var(--status-down)`)
- Label text retains `opacity: 0.7` from the base `.chip-label` rule (softer than the count)
- All existing frontend tests pass with zero regressions
- TypeScript typecheck passes

## Validation Commands
- `cd frontend && npm test` - Run frontend tests with zero regressions
- `cd frontend && npm run typecheck` - TypeScript type checking passes
- `cd backend && julia --project=. test/runtests.jl` - Run backend tests with zero regressions

## Notes
- CSS variables `--status-up`, `--status-issues`, `--status-maintenance`, `--status-down` are defined in `quantum-theme.css` `:root`. Verify exact variable names before writing rules.
- The base `.chip-label` rule sets `opacity: 0.7` — this applies on top of the color, giving a slightly muted label vs the bold count. This is intentional for visual hierarchy.
- No backend changes required — this is a pure CSS change.
- No TypeScript/template changes required — the class structure in EquipmentView already uses the correct status-variant classes.
