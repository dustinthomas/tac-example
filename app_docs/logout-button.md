# Logout Button

## Overview

The logout button provides authenticated users a way to explicitly sign out from any protected page. Before this feature, the only way to lose auth was token expiry or manually clearing localStorage — both poor UX and a security gap.

Clicking the button clears auth state and redirects to `/login`. The button is styled with the QCI Quantum theme (cyan border on dark navy background) and appears in the top-right corner of every protected view's header.

## Architecture

**No backend changes required.** Logout is a purely frontend operation.

### Components

- **`frontend/src/components/AppHeader.ts`** — Shared header bar rendered at the top of all protected views. Contains the QCI Foundry Services title (left) and the logout button (right).

### Integration Points

- **`frontend/src/stores/auth.ts`** — `authStore.logout()` clears `token` and `user` from Pinia state and `localStorage`.
- **`frontend/src/router.ts`** — Navigation guards redirect unauthenticated users to `/login`. After logout, `router.push('/login')` triggers this guard on any subsequent protected navigation.
- **`frontend/src/views/DashboardView.ts`** — Renders `<AppHeader />` at the top of the glass panel.
- **`frontend/src/views/EquipmentView.ts`** — Renders `<AppHeader />` at the top of the main content container.

### Styling

CSS classes added to `backend/public/css/quantum-theme.css`:

| Class | Purpose |
|---|---|
| `.app-header` | Flex row, space-between, dark navy glassmorphism bar |
| `.app-header__title` | QCI branding text, Raleway font, uppercase |
| `.logout-btn` | Cyan border button, transparent background |
| `.logout-btn:hover` | Subtle cyan fill on hover |

## Usage

### UI

1. Log in as any authenticated user (admin or operator).
2. The header bar appears at the top of the Dashboard and Equipment pages.
3. Click **LOGOUT** in the top-right corner.
4. Auth state is cleared and the browser navigates to `/login`.

### Logout Flow (code)

```typescript
// AppHeader.ts — setup()
function handleLogout() {
  authStore.logout()       // clears token + user from state and localStorage
  router.push('/login')    // redirect to login page
}
```

The `logout()` method is idempotent: it sets auth refs to `null` regardless of current state, so clicking logout with an already-expired token works correctly.

## Configuration

No environment variables or additional configuration required. The feature uses existing auth infrastructure:
- `authStore.logout()` — already implemented in `frontend/src/stores/auth.ts`
- Router guard — already implemented in `frontend/src/router.ts`

## Testing

### Automated Tests

- **`frontend/src/__tests__/components/AppHeader.spec.ts`** — Unit tests for the `AppHeader` component:
  - Renders `.app-header` element
  - Renders button with class `logout-btn` and text `LOGOUT`
  - Clicking the button calls `authStore.logout()`
  - After click, `authStore.isAuthenticated` is `false`
  - After click, `localStorage.getItem('token')` is `null`
  - After click, router navigates to `/login`

- **`frontend/src/__tests__/views/DashboardView.spec.ts`** — Updated to account for `AppHeader` being rendered inside the view.
- **`frontend/src/__tests__/views/EquipmentView.spec.ts`** — Updated to account for `AppHeader` being rendered inside the view.

Run the test suite:

```bash
cd frontend && npm test
```

### Manual Testing

1. Start the backend: `cd backend && julia --project=. src/App.jl`
2. Build the frontend: `cd frontend && npm run build`
3. Navigate to `http://localhost:8000` and log in as `admin` / `admin123`
4. Confirm the logout button appears in the header on the Dashboard page
5. Navigate to the Equipment page — confirm logout button also appears there
6. Click **LOGOUT** — confirm redirect to `/login`
7. Confirm `localStorage.getItem('token')` returns `null` in browser DevTools
8. Navigate directly to `/dashboard` — confirm redirect back to `/login` (router guard active)
