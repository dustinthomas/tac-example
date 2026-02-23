# Feature: Equipment Status Card Layout Redesign

## Metadata
issue_number: `the`
adw_id: `Equipment`
issue_json: `Status`

## Feature Description
Redesign the Equipment Status page from a flat data table layout into a visually rich card-based grid layout that groups equipment by fab area. Each equipment item is displayed as a card showing its name, status badge, criticality, bay, last updated time, and most recent comment. Area sections act as collapsible or labeled groupings with a header row showing the area name and a mini status summary for that area. The overall page retains the top-level status summary bar, filter controls, and AppHeader — only the equipment list rendering changes from a `<table>` to a responsive card grid.

## User Story
As a fab operator
I want to see equipment organized into visual cards grouped by area
So that I can quickly scan equipment health at a glance without reading rows in a dense table

## Problem Statement
The current equipment list is rendered as a wide data table. On larger screens it works, but visually it is hard to parse quickly — especially when scanning for DOWN or ISSUES equipment across multiple areas. Operators need a faster, more spatial overview that mirrors how the physical fab is organized.

## Solution Statement
Replace the `<table>` section inside `EquipmentView.ts` with a card-grid layout. Equipment cards will be grouped under area section headers. Each card shows: equipment name, description, status badge, criticality badge, bay label, last updated timestamp, and last comment. The filter bar and status summary cards remain unchanged. Styling is added to `quantum-theme.css`. The `/frontend-design` skill will be used to generate the card component and updated view template.

## Relevant Files

- `frontend/src/views/EquipmentView.ts` — Main view to be refactored; table replaced with card grid
- `frontend/src/components/StatusBadge.ts` — Reusable status badge used inside each equipment card
- `frontend/src/components/AppHeader.ts` — Already used in the view, no changes needed
- `frontend/src/types/index.ts` — Equipment and StatusSummary types; may add a grouped-equipment computed helper type
- `frontend/src/stores/equipment.ts` — Pinia store providing equipment list; read-only for this feature
- `backend/public/css/quantum-theme.css` — QCI theme CSS; new card layout styles added here
- `frontend/src/__tests__/EquipmentView.test.ts` — Frontend unit tests; update to cover card rendering

### New Files
- `frontend/src/components/EquipmentCard.ts` — New reusable card component for a single equipment item

## Implementation Plan

### Phase 1: Foundation
- Create the `EquipmentCard` component that accepts a single `Equipment` object as a prop and renders its details in a card format matching the target layout
- Add CSS classes for the card grid, area section headers, and card internals to `quantum-theme.css`

### Phase 2: Core Implementation
- Refactor `EquipmentView.ts` to:
  - Add a `groupedEquipment` computed property that groups `filteredEquipment` by `area`
  - Replace the `<table>` block with an area-grouped card grid using `v-for` over areas and `EquipmentCard` inside each area section
  - Import and register `EquipmentCard`

### Phase 3: Integration
- Update frontend tests in `EquipmentView.test.ts` to assert card elements render instead of table rows
- Run typecheck and full test suite to confirm zero regressions

## Step by Step Tasks

### Step 1: Use `/frontend-design` skill to generate the card layout UI
- Invoke the `/frontend-design` skill with the following brief:
  - **Component:** `EquipmentCard.ts` — a single equipment card for a no-bundler Vue 3 `defineComponent()` setup
  - **Layout target:** Match the screenshot — glassmorphism card with: top-left equipment name + description, top-right status badge, a row of metadata chips (area badge, bay, criticality badge), bottom row with "Updated by / time" and truncated last comment
  - **Design tokens:** Use QCI quantum theme — dark navy background `#1E204B`, cyan accent `#00BCD4`, Raleway font, glassmorphism card (semi-transparent, blur, cyan border)
  - **Props:** `equipment: Equipment` (imported from `../types/index.js`)
  - **No external imports** beyond `vue` and local types
  - Save output to `frontend/src/components/EquipmentCard.ts`

### Step 2: Add card grid CSS to quantum-theme.css
- Open `backend/public/css/quantum-theme.css`
- Add styles for:
  - `.equipment-area-section` — area group wrapper with a labeled header bar (area name + mini count chips)
  - `.area-section-header` — styled header row with area name and status mini-summary
  - `.equipment-card-grid` — CSS grid, `repeat(auto-fill, minmax(320px, 1fr))`, gap 16px
  - `.equipment-card` — glassmorphism card: `background: rgba(34,35,84,0.7)`, `border: 1px solid rgba(0,188,212,0.2)`, `backdrop-filter: blur(8px)`, `border-radius: 12px`, padding 20px
  - `.equipment-card:hover` — subtle cyan border glow
  - `.card-header` — flex row: name+description left, status badge right
  - `.card-meta` — flex row of chips: area badge, bay, criticality
  - `.card-footer` — muted text row: updated_by + formatDate + last_comment truncated to 1 line

### Step 3: Add `groupedEquipment` computed to EquipmentView.ts
- In `EquipmentView.ts` `setup()`, add a computed that groups `filteredEquipment` by area:
  ```ts
  const groupedEquipment = computed(() => {
    const groups: Record<string, Equipment[]> = {}
    for (const eq of filteredEquipment.value) {
      if (!groups[eq.area]) groups[eq.area] = []
      groups[eq.area].push(eq)
    }
    return groups
  })
  ```
- Import `Equipment` type if not already imported
- Add `groupedEquipment` to the returned object

### Step 4: Refactor the template in EquipmentView.ts
- Remove the `<div class="equipment-table-wrapper">` block and the `<table>` entirely
- Replace with a card-grid section:
  ```html
  <div v-if="!equipmentStore.loading" class="equipment-areas">
    <div v-for="area in areas" :key="area" v-if="groupedEquipment[area]?.length" class="equipment-area-section">
      <div class="area-section-header">
        <span class="area-name">{{ area }}</span>
        <span class="area-count">{{ groupedEquipment[area].length }} units</span>
      </div>
      <div class="equipment-card-grid">
        <EquipmentCard
          v-for="eq in groupedEquipment[area]"
          :key="eq.id"
          :equipment="eq"
        />
      </div>
    </div>
  </div>
  ```
- Add `EquipmentCard` to the `components` option and import it from `'../components/EquipmentCard.js'`

### Step 5: Update frontend tests
- Open `frontend/src/__tests__/EquipmentView.test.ts`
- Remove or update assertions that check for `<table>`, `<tr>`, or `<td>` elements
- Add assertions that:
  - Card elements with class `equipment-card` are rendered for each equipment item
  - Area section headers are rendered
  - Status badge is present inside each card

### Step 6: Build and validate
- Run all validation commands listed below

## Testing Strategy

### Unit Tests
- `EquipmentCard.ts`: render with each status type and assert badge class is correct
- `EquipmentView.ts`: mock store with 2 areas × 2 items each; assert 2 area sections and 4 cards render; assert filter by area hides correct section

### Integration Tests
- Full page render with mocked Pinia store; filter by status; confirm filtered cards update correctly

### Edge Cases
- No equipment in an area → area section should not render (v-if guard)
- All equipment filtered out → show a "No equipment found" message
- Equipment with null/empty last_comment → card footer renders gracefully (show dash or empty)
- Very long equipment names → truncate with CSS `overflow: hidden; text-overflow: ellipsis`

## Acceptance Criteria
- [ ] Equipment Status page renders equipment as cards instead of a table
- [ ] Cards are grouped by fab area (Lithography, Etching, Deposition, Metrology)
- [ ] Each area has a labeled section header showing the area name and unit count
- [ ] Each card displays: name, description, status badge, criticality badge, bay, updated_by, formatted time, last comment
- [ ] Existing filters (status, area, search) still work and update the card grid reactively
- [ ] Existing status summary row (Operational / With Issues / Maintenance / Down counts) is unchanged
- [ ] Design matches QCI quantum theme: glassmorphism cards, cyan accents, dark navy
- [ ] TypeScript typechecks with zero errors
- [ ] All frontend tests pass with zero regressions
- [ ] All backend tests pass with zero regressions

## Validation Commands
- `cd frontend && npm run build` — Transpile TypeScript; must complete with zero errors
- `cd frontend && npm run typecheck` — TypeScript type checking passes
- `cd frontend && npm test` — Run frontend tests with zero regressions
- `cd backend && julia --project=. test/runtests.jl` — Run backend tests with zero regressions

## Notes
- The target layout (from the reference screenshot) shows a card grid grouped by area. The image reveals: cards have a subtle glassmorphism style consistent with the existing QCI quantum theme already applied to the rest of the app.
- The `areas` array is already available in `EquipmentView.ts` — iterate over it to control area render order deterministically rather than using `Object.keys(groupedEquipment)`.
- `EquipmentCard.ts` should follow the same no-SFC `defineComponent()` + template string pattern used by all other components in this project.
- Do NOT change any backend routes, database schema, or the Pinia store's data shape — this is a pure frontend layout change.
- The `/frontend-design` skill should be invoked for Step 1 to get a high-quality, on-theme card design before wiring it into the view.
