# Feature: Equipment Status Layout Redesign

## Feature Description
Reorganize the Equipment Status page layout so the status summary stats (Operational, With Issues, Maintenance, Down counts) move from a separate full-width card grid below the page title into an inline row on the right side of the header section. This creates a compact, information-dense header that mirrors the reference design: title + subtitle on the left, colored stat chips on the right — all in one header row. The filter bar and table remain below unchanged.

## User Story
As a fab operator
I want to see the equipment status summary counts in line with the page header
So that I can quickly scan overall equipment health at a glance without scrolling past large cards before reaching the filter and table

## Problem Statement
The current layout places four large status-summary cards in their own full-width section between the page header and the filter bar. This pushes the actionable table further down the page and wastes vertical space with redundant visual weight. The reference design collapses these stats into compact inline chips positioned at the right edge of the header row, matching the actual design intent.

## Solution Statement
Restructure the `.equipment-header` element to use `display: flex; justify-content: space-between` so the title/subtitle block sits on the left and a compact row of four stat chips sits on the right. Replace the existing `.status-summary` grid section with these inline chips inside the header. Update CSS to style the inline chips (`.status-chips`) and remove the `.status-summary` block styles (or repurpose them). Tests that target `.status-card` selectors must be updated to match the new chip element structure.

## Relevant Files

- **`frontend/src/views/EquipmentView.ts`** — Contains the entire Equipment Status view template and logic. The HTML structure and class names change here. Status summary moves from its own `<div class="status-summary">` section into the `.equipment-header` row.
- **`backend/public/css/quantum-theme.css`** — Contains all existing CSS for `.equipment-header`, `.status-summary`, `.status-card`, and `.filter-bar`. New `.status-chips` and `.status-chip` rules added; `.status-summary` / `.status-card` rules removed or replaced.
- **`frontend/src/__tests__/views/EquipmentView.spec.ts`** — Unit tests that assert `.status-card` count and `.count` text. Selectors must be updated to match the new chip class names (`.status-chip`, `.chip-count`).

### New Files
_(none — no new files required)_

## Implementation Plan

### Phase 1: Foundation
Update CSS in `quantum-theme.css` to:
- Make `.equipment-header` use `justify-content: space-between` and `align-items: center`
- Add `.status-chips` flex container for the right-side stat row
- Add `.status-chip` rule for individual compact chips (number + label stacked, colored border/text per status class)
- Remove or comment out the old `.status-summary` grid and `.status-card` rules

### Phase 2: Core Implementation
Rewrite the template in `EquipmentView.ts`:
- Merge the `<div class="status-summary">` block into `.equipment-header`, placing `<div class="status-chips">` as the right child
- Each chip: `<div class="status-chip up|issues|maintenance|down"><span class="chip-count">{{ n }}</span><span class="chip-label">Label</span></div>`
- Remove the now-redundant standalone `.status-summary` section

### Phase 3: Integration
Update `EquipmentView.spec.ts` tests:
- Replace `.status-card` selector → `.status-chip`
- Replace `.status-card .count` selector → `.status-chip .chip-count`
- Verify all other tests (filter, search, table rows) are unaffected

## Step by Step Tasks

### Step 1: Update CSS — restyle header and add chip styles
- Open `backend/public/css/quantum-theme.css`
- Find `.equipment-header` rule; add `justify-content: space-between; align-items: center;` (it already has `display: flex`)
- Add new rules after `.equipment-header p`:
  ```css
  .status-chips {
    display: flex;
    gap: 12px;
    align-items: center;
    flex-shrink: 0;
  }

  .status-chip {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 8px 16px;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.1);
    background: rgba(255,255,255,0.04);
    min-width: 68px;
    cursor: default;
    transition: background 0.2s;
  }

  .status-chip:hover { background: rgba(255,255,255,0.08); }

  .status-chip .chip-count {
    font-size: 1.5rem;
    font-weight: 700;
    line-height: 1.1;
  }

  .status-chip .chip-label {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    opacity: 0.7;
    margin-top: 2px;
  }

  .status-chip.up .chip-count { color: var(--status-up); }
  .status-chip.up { border-color: rgba(46, 204, 113, 0.3); }

  .status-chip.issues .chip-count { color: var(--status-issues); }
  .status-chip.issues { border-color: rgba(253, 216, 53, 0.3); }

  .status-chip.maintenance .chip-count { color: var(--status-maintenance); }
  .status-chip.maintenance { border-color: rgba(230, 126, 34, 0.3); }

  .status-chip.down .chip-count { color: var(--status-down); }
  .status-chip.down { border-color: rgba(231, 76, 60, 0.3); }
  ```
- Remove (or comment out) the old `.status-summary`, `.status-card`, `.status-card:hover`, `.status-card .count`, `.status-card .label`, and per-variant `.status-card.*` rules
- In the responsive media query, remove `.status-summary { grid-template-columns: ... }` and add `.status-chips { flex-wrap: wrap; gap: 8px; }` instead

### Step 2: Update EquipmentView.ts template — move status chips into header
- Open `frontend/src/views/EquipmentView.ts`
- Replace the `.equipment-header` block and the following `.status-summary` block with a merged structure:

  **Before (two separate sections):**
  ```html
  <div class="equipment-header">
    <svg .../>
    <div>
      <h1>Equipment Status</h1>
      <p>Real-time monitoring of fab equipment</p>
    </div>
  </div>

  <div class="status-summary">
    <div class="status-card up">
      <div class="count">{{ statusSummary.up }}</div>
      <div class="label">Operational</div>
    </div>
    ...
  </div>
  ```

  **After (status chips inline in header):**
  ```html
  <div class="equipment-header">
    <div style="display:flex;align-items:center;gap:14px;">
      <svg .../>
      <div>
        <h1>Equipment Status</h1>
        <p>Real-time monitoring of fab equipment across all areas</p>
      </div>
    </div>
    <div class="status-chips">
      <div class="status-chip up">
        <span class="chip-count">{{ statusSummary.up }}</span>
        <span class="chip-label">Operational</span>
      </div>
      <div class="status-chip issues">
        <span class="chip-count">{{ statusSummary.issues }}</span>
        <span class="chip-label">With Issues</span>
      </div>
      <div class="status-chip maintenance">
        <span class="chip-count">{{ statusSummary.maintenance }}</span>
        <span class="chip-label">Maintenance</span>
      </div>
      <div class="status-chip down">
        <span class="chip-count">{{ statusSummary.down }}</span>
        <span class="chip-label">Down</span>
      </div>
    </div>
  </div>
  ```
- Remove the standalone `<div class="status-summary">...</div>` section entirely

### Step 3: Update EquipmentView.spec.ts tests
- Open `frontend/src/__tests__/views/EquipmentView.spec.ts`
- In `'renders status summary cards'` test: change `.status-card` → `.status-chip`, update description to "renders status summary chips"
- In `'shows correct status summary counts'` test: change `.status-card .count` → `.status-chip .chip-count`
- Verify no other test references `.status-card` or `.status-summary`

### Step 4: Build and validate
- Run `cd frontend && npm run build` to transpile TS → JS
- Run `cd frontend && npm run typecheck` to verify zero type errors
- Run `cd frontend && npm test` to verify all tests pass
- Run `cd backend && julia --project=. test/runtests.jl` to verify backend tests pass (layout change should not affect backend)

## Testing Strategy

### Unit Tests
- `'renders status summary chips'` — assert 4 `.status-chip` elements exist
- `'shows correct status summary counts'` — assert `.status-chip .chip-count` values match expected counts (3, 1, 1, 1)
- All existing filter/search/table/count tests remain unchanged

### Integration Tests
- Visual inspection in browser: header row shows title on left, 4 colored chips on right
- Filter bar and table appear immediately below, no extra whitespace from removed card section

### Edge Cases
- Responsive: on narrow viewports chips wrap cleanly within the header or stack below the title
- Zero counts display as "0" (not blank)
- When all equipment is UP, issues/maintenance/down chips show 0

## Acceptance Criteria
- [ ] Status summary counts appear as compact chips in the right side of the `.equipment-header` row, not in a separate section below
- [ ] The standalone `.status-summary` grid section is removed from the template
- [ ] Each chip shows the correct count and label with appropriate status color
- [ ] The filter bar and table are visually closer to the top — no large card section between header and filters
- [ ] All 48 frontend unit tests pass with zero regressions
- [ ] TypeScript typecheck passes with zero errors
- [ ] Backend Julia tests pass with zero regressions
- [ ] Layout matches the reference image (title+subtitle left, stat chips right, filter bar below)

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
cd frontend && npm run build
cd frontend && npm run typecheck
cd frontend && npm test
cd backend && julia --project=. test/runtests.jl
```

- `cd frontend && npm run build` — TypeScript compiles to JS with zero errors
- `cd frontend && npm run typecheck` — TypeScript type checking passes
- `cd frontend && npm test` — All frontend unit tests pass (expected: 48+)
- `cd backend && julia --project=. test/runtests.jl` — Backend tests pass with zero regressions

## Notes
- The `.equipment-header` already has `display: flex` in the current CSS — only `justify-content` and `align-items` need to be added/changed.
- The SVG icon in the header currently sits directly inside `.equipment-header`. After this change it should be wrapped with the title/subtitle `<div>` in a flex group so the icon stays beside the text, not floating left alone.
- The old `.status-card` CSS rules can be deleted entirely — no other view uses them.
- No backend changes are required for this purely frontend layout change.
- Keep the `statusSummary` computed property unchanged — same data, different presentation.
