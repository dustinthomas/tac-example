# Feature: Move Logout Button to Top-Right Corner

## Feature Description
Relocate the logout button from inside the `AppHeader` component (which sits within the glass panel content area) to a fixed position in the top-right corner of the viewport. This matches the design shown in the reference image: a small "LOGOUT" button pinned to the top-right, always visible regardless of scroll position, outside the main content flow.

## User Story
As an authenticated user
I want to see the logout button fixed in the top-right corner of the screen
So that I can always access it quickly without it being buried inside the page header

## Problem Statement
The current logout button lives inside `AppHeader`, which is rendered inside `DashboardView`'s glass panel. This makes it feel like a secondary element within the page content rather than a persistent UI control. The desired UX places logout as a global, always-accessible action pinned to the viewport corner.

## Solution Statement
Remove the logout button from `AppHeader` and introduce a new `LogoutButton` component rendered at the `App` root level (alongside `QuantumBackground` and `DockNav`). The button uses `position: fixed; top: 1rem; right: 1rem` so it always appears in the top-right corner. It only renders when the user is authenticated. The `AppHeader` component loses its logout button but retains its title text (or can be removed from `DashboardView` if no longer needed).

## Relevant Files

- `frontend/src/components/AppHeader.ts` — currently contains the logout button; the button will be removed from here
- `frontend/src/App.ts` — root component; the new `LogoutButton` component will be added here so it renders globally
- `frontend/src/views/DashboardView.ts` — uses `AppHeader`; may need update if `AppHeader` is simplified or removed
- `backend/public/css/quantum-theme.css` — contains `.app-header` and `.logout-btn` styles; new fixed-position styles added, old header button styles removed/updated
- `frontend/src/__tests__/components/AppHeader.spec.ts` — tests for `AppHeader`; update to reflect logout button removal
- `frontend/src/__tests__/App.spec.ts` — root App tests; update to cover `LogoutButton` rendering

### New Files
- `frontend/src/components/LogoutButton.ts` — new standalone component with fixed positioning and auth-conditional rendering
- `frontend/src/__tests__/components/LogoutButton.spec.ts` — unit tests for the new `LogoutButton` component

## Implementation Plan
### Phase 1: Foundation
Create the `LogoutButton` component with its own template, auth store integration, and router navigation. Add CSS for fixed top-right positioning.

### Phase 2: Core Implementation
- Wire `LogoutButton` into `App.ts` so it renders globally on all authenticated views.
- Remove the logout button from `AppHeader`; simplify or remove `AppHeader` from `DashboardView` accordingly.

### Phase 3: Integration
Update tests: add `LogoutButton` spec, update `AppHeader` spec (button no longer present), update `App.spec.ts` to verify `LogoutButton` presence.

## Step by Step Tasks

### Step 1: Create LogoutButton component
- Create `frontend/src/components/LogoutButton.ts`
- Use `defineComponent` with `setup()` importing `useAuthStore` and `useRouter`
- Conditionally render the button only when `authStore.isAuthenticated` is true (use `v-if`)
- On click: call `authStore.logout()` then `router.push('/login')`
- Template: `<button class="logout-btn logout-btn--fixed" @click="handleLogout">LOGOUT</button>` wrapped in a `<template v-if="isAuthenticated">`

### Step 2: Add CSS for fixed logout button
- In `backend/public/css/quantum-theme.css`, add `.logout-btn--fixed` rule:
  ```css
  .logout-btn--fixed {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 1000;
  }
  ```
- Keep existing `.logout-btn` base styles (border, color, padding, font, cursor, transition) so the modifier class only adds positioning

### Step 3: Register LogoutButton in App.ts
- Import `LogoutButton` from `./components/LogoutButton.js`
- Add to `components` object
- Add `<LogoutButton />` to the template (alongside `<QuantumBackground />` and `<DockNav />`)

### Step 4: Remove logout button from AppHeader
- In `frontend/src/components/AppHeader.ts`:
  - Remove the `useRouter` import and `handleLogout` function
  - Remove the `useAuthStore` import
  - Remove `<button class="logout-btn" @click="handleLogout">LOGOUT</button>` from the template
  - Simplify `setup()` to return `{}`
- The `.app-header` element now only shows the title, or can be further simplified

### Step 5: Update AppHeader tests
- In `frontend/src/__tests__/components/AppHeader.spec.ts`:
  - Remove tests for logout button presence, text, click behavior, auth state, localStorage clearing, and router navigation (all 5 logout-related tests)
  - Keep only the test that checks `.app-header` element renders

### Step 6: Create LogoutButton tests
- Create `frontend/src/__tests__/components/LogoutButton.spec.ts`
- Test cases:
  - Does not render when not authenticated
  - Renders button with class `logout-btn` when authenticated
  - Button text is `LOGOUT`
  - Clicking calls `authStore.logout()`
  - After click, `authStore.isAuthenticated` is false
  - After click, localStorage token is null
  - After click, router navigates to `/login`

### Step 7: Update App.spec.ts
- Verify `LogoutButton` is registered in the App component
- Add a test that confirms `<LogoutButton />` is present in the App template when authenticated

### Step 8: Build and validate
- Run `cd frontend && npm run build` — ensure TypeScript compiles with zero errors
- Run `cd frontend && npm run typecheck` — type checking passes
- Run `cd frontend && npm test` — all tests pass with zero regressions
- Run `cd backend && julia --project=. test/runtests.jl` — backend tests unchanged

## Testing Strategy
### Unit Tests
- `LogoutButton.spec.ts`: full coverage of rendering (authenticated/unauthenticated), click behavior, auth state mutation, localStorage, and routing
- `AppHeader.spec.ts`: stripped to only verify the `.app-header` element still renders

### Integration Tests
- `App.spec.ts`: verify `LogoutButton` is wired into root App component

### Edge Cases
- Button must NOT render on login page (user not authenticated) — handled by `v-if="isAuthenticated"`
- Button must remain visible when content scrolls — handled by `position: fixed`
- z-index must not be obscured by DockNav or QuantumBackground

## Acceptance Criteria
- [ ] Logout button appears in the top-right corner of the viewport at all times when authenticated
- [ ] Logout button is NOT visible on the login page (unauthenticated)
- [ ] Clicking logout clears auth state and redirects to `/login`
- [ ] `AppHeader` no longer contains a logout button
- [ ] All frontend tests pass (zero regressions)
- [ ] TypeScript typecheck passes
- [ ] Backend tests unchanged and passing

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd frontend && npm run build` - TypeScript compiles to JS with zero errors
- `cd frontend && npm run typecheck` - TypeScript type checking passes
- `cd frontend && npm test` - Run frontend tests with zero regressions
- `cd backend && julia --project=. test/runtests.jl` - Run backend tests with zero regressions

## Notes
- The `AppHeader` component can be further simplified or eventually removed from `DashboardView` if the title is redundant with the page's own `<h1>`. For this feature, leave `AppHeader` in place but strip the logout button from it.
- The `position: fixed` button will float above all other content. Ensure `z-index: 1000` is high enough to clear the glass panel but low enough not to conflict with any modal layers added in the future.
- The existing `.logout-btn` base styles stay intact; only a modifier class adds the fixed positioning. This keeps backward compatibility if the class is tested by name.
