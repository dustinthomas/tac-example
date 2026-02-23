# Feature: Logout Button in Dashboard Header

## Feature Description
Add a logout button to the dashboard header bar so authenticated users can sign out of the application. The button appears in the top-right area of the dashboard header, clears the auth token on click, and redirects the user to the login page. It is styled consistently with the QCI Quantum theme (cyan accent on dark navy background).

## User Story
As an authenticated operator or admin
I want to click a logout button in the dashboard header
So that I can securely sign out of the application from any protected page

## Problem Statement
Currently, there is no way for a user to explicitly log out of the application through the UI. The only way to lose auth is via token expiry or manual localStorage clearing — both poor UX and a security gap.

## Solution Statement
Add a `LogoutButton` component rendered inside a shared `AppHeader` component. The header appears at the top of all protected views. On click, the button calls `authStore.logout()` (which clears token + user from state and localStorage) and then uses the router to redirect to `/login`. The button is styled with a cyan border on a dark navy background per the QCI Quantum theme.

## Relevant Files

- `frontend/src/stores/auth.ts` — Contains `logout()` which clears token/user from state and localStorage. This is the primary action triggered by the button.
- `frontend/src/router.ts` — Navigation guards redirect unauthenticated users to login. After logout, `router.push('/login')` is called.
- `frontend/src/views/DashboardView.ts` — The main protected view. The header area currently has a `.header` div with `h1` + `p`; the logout button will be added to a top-right slot in this header.
- `frontend/src/views/EquipmentView.ts` — Another protected view. Will also receive the shared header for consistency.
- `frontend/src/App.ts` — Root component. May be used as an alternative placement for the shared header.
- `frontend/src/__tests__/` — Existing frontend test directory (vitest).

### New Files
- `frontend/src/components/AppHeader.ts` — New shared header component containing the QCI branding bar and the logout button, used across all protected views.
- `frontend/src/__tests__/AppHeader.test.ts` — Unit tests for the AppHeader component (logout action, router redirect, rendering).

## Implementation Plan

### Phase 1: Foundation
Create the `AppHeader` component with the logout button. It imports `useAuthStore` and `useRouter`, calls `logout()` then `router.push('/login')` on click. Style with inline CSS consistent with the QCI Quantum theme.

### Phase 2: Core Implementation
Integrate `AppHeader` into `DashboardView` and `EquipmentView` by replacing or wrapping the existing per-page header markup. Ensure the button is positioned in the top-right corner of the header bar.

### Phase 3: Integration
Write unit tests for `AppHeader`. Verify logout clears store state, removes localStorage keys, and navigates to `/login`. Run full test suite to confirm zero regressions.

## Step by Step Tasks

### Step 1: Create AppHeader Component
- Create `frontend/src/components/AppHeader.ts`
- Import `defineComponent` from `'vue'`, `useRouter` from `'vue-router'`, and `useAuthStore` from `'../stores/auth.js'`
- In `setup()`, call `const authStore = useAuthStore()` and `const router = useRouter()`
- Define `handleLogout()`: call `authStore.logout()` then `router.push('/login')`
- Template: a `<header class="app-header">` containing a left-side title span and a right-side logout button
- Logout button: `<button class="logout-btn" @click="handleLogout">LOGOUT</button>`
- Add CSS to `backend/public/css/quantum-theme.css` (no SFC, so no `<style>` tags):
  - `.app-header`: `display: flex; justify-content: space-between; align-items: center; padding: 12px 24px; background: rgba(30,32,75,0.85); border-bottom: 1px solid rgba(255,255,255,0.08); backdrop-filter: blur(12px);`
  - `.app-header__title`: `color: #F4F5F9; font-family: 'Raleway', sans-serif; font-size: 1rem; letter-spacing: 0.1em; text-transform: uppercase;`
  - `.logout-btn`: `border: 1px solid #00BCD4; color: #00BCD4; background: transparent; padding: 6px 16px; border-radius: 4px; cursor: pointer; font-family: 'Raleway', sans-serif; font-size: 0.8rem; letter-spacing: 0.08em; text-transform: uppercase; transition: background 0.2s;`
  - `.logout-btn:hover`: `background: rgba(0, 188, 212, 0.12);`

### Step 2: Integrate AppHeader into DashboardView
- Edit `frontend/src/views/DashboardView.ts`
- Import `AppHeader` from `'../components/AppHeader.js'`
- Register it in `components: { AppHeader }`
- Replace the existing `<div class="header">` block with `<AppHeader />` (the AppHeader component provides its own header bar; the QCI Foundry Services title and description move inside AppHeader or remain as a sub-section below it)
- Specifically: add `<AppHeader />` at the top of the `.glass-panel`, keeping the existing `<h1>`, `.quantum-line`, and `<p>` below it as page-specific content

### Step 3: Integrate AppHeader into EquipmentView
- Edit `frontend/src/views/EquipmentView.ts`
- Import and register `AppHeader` the same way as DashboardView
- Place `<AppHeader />` at the top of the main content container (above the equipment header section)

### Step 4: Write Unit Tests for AppHeader
- Create `frontend/src/__tests__/components/AppHeader.spec.ts` (match the existing test directory structure)
- Use vitest + `@vue/test-utils`, follow the DockNav.spec.ts pattern
- Create a `makeRouter()` helper that creates an isolated `createRouter` with the project routes
- Call `setActivePinia(createPinia())` in `beforeEach`, clear localStorage
- Mount with `global: { plugins: [pinia, router] }`
- Test cases:
  1. Component renders `.app-header` element
  2. Renders a button with class `logout-btn`
  3. Button text is `LOGOUT`
  4. Clicking the button calls `authStore.logout()` (spy on `authStore.logout`)
  5. After click, `authStore.isAuthenticated` is `false`
  6. After click, `localStorage.getItem('token')` is `null`
  7. After click, router navigates to `/login` (`router.currentRoute.value.path === '/login'`)

### Step 5: Build and Validate
- Run `cd frontend && npm run build` — confirm TypeScript compiles with no errors
- Run `cd frontend && npm run typecheck` — confirm zero type errors
- Run `cd frontend && npm test` — confirm all tests pass including new AppHeader tests
- Run `cd backend && julia --project=. test/runtests.jl` — confirm backend tests unchanged

## Testing Strategy

### Unit Tests
- `AppHeader.test.ts`:
  - Renders logout button with correct label
  - Calls `authStore.logout()` on button click
  - Calls `router.push('/login')` on button click
  - Button has expected CSS class for QCI styling

### Integration Tests
- Manual: Log in as `admin` → confirm logout button appears → click → confirm redirect to `/login` → confirm localStorage `token` and `user` are cleared → confirm navigating to `/dashboard` redirects back to `/login`

### Edge Cases
- Clicking logout when token is already missing (e.g., expired): `logout()` is idempotent — it sets refs to null regardless; router still navigates to `/login`
- Rapid double-click: no issue since logout is synchronous and navigation is immediate
- Logout button visible on both DashboardView and EquipmentView

## Acceptance Criteria
- [ ] Logout button is visible in the top-right area of the header on the Dashboard page
- [ ] Logout button is visible in the top-right area of the header on the Equipment page
- [ ] Clicking the button calls `authStore.logout()` (clears `token` and `user` from state and localStorage)
- [ ] After logout, the user is redirected to `/login`
- [ ] Button uses cyan accent color (`#00BCD4`) border on dark navy background, consistent with QCI Quantum theme
- [ ] Button has hover state (subtle cyan background)
- [ ] All existing frontend tests pass (zero regressions)
- [ ] TypeScript type checking passes
- [ ] Backend tests unchanged

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd frontend && npm run build` - TypeScript compiles without errors
- `cd frontend && npm run typecheck` - TypeScript type checking passes
- `cd frontend && npm test` - Run frontend tests with zero regressions (including new AppHeader tests)
- `cd backend && julia --project=. test/runtests.jl` - Run backend tests with zero regressions

## Notes
- No backend changes are required. Logout is a purely frontend operation (clearing localStorage + redirecting).
- The `authStore.logout()` method already exists and is complete — no store changes needed.
- The router guard already handles unauthenticated access by redirecting to `/login` — no router changes needed.
- Future: consider adding a user display name/role in the header beside the logout button (out of scope for this feature).
- Follow the no-SFC convention: components use `defineComponent()` with template strings in `.ts` files.
