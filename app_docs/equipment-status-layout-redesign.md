# Equipment Status Layout Redesign

## Overview

Reorganizes the Equipment Status page so the four status summary counts (Operational, With Issues, Maintenance, Down) appear as compact inline chips on the right side of the page header, rather than in a separate full-width card grid between the header and filter bar. This eliminates wasted vertical space and puts actionable data (the filter bar and equipment table) closer to the top of the page.

## Architecture

This is a purely frontend change — no backend routes or database tables are affected.

**Files changed:**

- `frontend/src/views/EquipmentView.ts` — Template restructured: `.status-summary` section removed; `.status-chips` container added inside `.equipment-header`
- `backend/public/css/quantum-theme.css` — Old `.status-summary` / `.status-card` rules removed; new `.status-chips` and `.status-chip` rules added
- `frontend/src/__tests__/views/EquipmentView.spec.ts` — Test selectors updated from `.status-card` / `.count` to `.status-chip` / `.chip-count`

## Usage

### UI Layout

The Equipment Status page header now uses `justify-content: space-between` to place two flex children side by side:

| Left | Right |
|------|-------|
| SVG icon + "Equipment Status" title + subtitle | Four colored stat chips |

Each chip displays:
- A large number (count) in the status color
- A small uppercase label below

### Chip Structure (HTML)

```html
<div class="equipment-header">
  <div style="display:flex;align-items:center;gap:14px;">
    <!-- SVG icon -->
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

### CSS Classes

| Class | Purpose |
|-------|---------|
| `.status-chips` | Flex row container for the four chips (right side of header) |
| `.status-chip` | Individual chip — column flex, padded, rounded border |
| `.status-chip.up` | Green border + count color (`var(--status-up)`) |
| `.status-chip.issues` | Yellow border + count color (`var(--status-issues)`) |
| `.status-chip.maintenance` | Orange border + count color (`var(--status-maintenance)`) |
| `.status-chip.down` | Red border + count color (`var(--status-down)`) |
| `.chip-count` | Large bold number |
| `.chip-label` | Small uppercase label |

Responsive: on narrow viewports, `.status-chips` wraps with `flex-wrap: wrap; gap: 8px`.

### Data Source

The `statusSummary` computed property in `EquipmentView.ts` is unchanged — it derives counts from the same `equipment` store data as before.

## Configuration

No environment variables or settings are required. This is a pure layout/style change.

## Testing

### Automated Tests (`frontend/src/__tests__/views/EquipmentView.spec.ts`)

| Test | What it checks |
|------|---------------|
| `renders status summary chips` | 4 `.status-chip` elements exist in the DOM |
| `shows correct status summary counts` | `.status-chip .chip-count` values match mock data (3 up, 1 issues, 1 maintenance, 1 down) |
| All other tests (filter, search, table rows) | Unchanged — no regressions |

Run frontend tests:

```bash
cd frontend && npm test
```

Expected: 48+ tests pass, zero failures.

### Manual Testing

1. Start the app: `sh ./scripts/start.sh`
2. Log in and navigate to **Equipment Status**
3. Verify the header row shows title/subtitle on the left and four colored chips on the right
4. Verify the filter bar and table appear immediately below with no large card section between them
5. Resize the browser to a narrow viewport — chips should wrap cleanly

### Typecheck & Build

```bash
cd frontend && npm run typecheck   # Zero type errors
cd frontend && npm run build       # Compiles TS → JS with zero errors
cd backend && julia --project=. test/runtests.jl  # Backend unaffected
```
