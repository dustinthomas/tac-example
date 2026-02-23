# Frontend Architecture: No-Bundler Vue 3 + TypeScript

## Motivation

IT policy prohibits Node.js as a production dependency. This architecture keeps Node/npm as a **dev-only tool** (on the agent VM) for TypeScript compilation and type checking. The production server (Genie.jl) serves only static `.js`, `.css`, and `.html` files — no Node process required.

## Architecture Overview

```
frontend/src/*.ts  →  tsc  →  backend/public/js/app/*.js  →  browser
                                backend/public/js/vendor/   →  browser (Vue, Pinia, Router)
                                backend/public/css/         →  browser (QCI theme)
                                backend/public/index.html   →  browser (import map + mount point)
```

**Key mechanism:** Browser import maps bridge TypeScript's module resolution (bare specifiers like `'vue'`) with the browser's need for actual file paths (`/js/vendor/vue.esm-browser.js`).

---

## Directory Structure

```
frontend/
├── package.json          # Dev-only deps: typescript, vue/pinia/router type declarations
├── tsconfig.json         # TypeScript config (paths, outDir → ../backend/public/js/app)
└── src/
    ├── main.ts           # App entry point (createApp, mount, install plugins)
    ├── App.ts            # Root component
    ├── router.ts         # Vue Router configuration
    ├── components/       # UI components (defineComponent .ts files)
    ├── stores/           # Pinia stores
    ├── views/            # Page-level components (routed views)
    └── types/            # Shared TypeScript interfaces and types

backend/public/
├── index.html            # Entry point: import map + <div id="app"> + <script type="module">
├── css/
│   └── quantum-theme.css # QCI theme (extracted from design reference)
└── js/
    ├── app/              # tsc output (GITIGNORED — rebuild from frontend/src/)
    │   ├── main.js
    │   ├── App.js
    │   ├── router.js
    │   ├── components/
    │   ├── stores/
    │   ├── views/
    │   └── types/
    └── vendor/           # Self-hosted ES modules (COMMITTED to git)
        ├── vue.esm-browser.js
        ├── vue.esm-browser.prod.js
        ├── pinia.esm-browser.js
        ├── vue-router.esm-browser.js
        └── vue-router.esm-browser.prod.js
```

---

## Vendor Libraries

Self-hosted ESM browser builds, downloaded once and committed to git.

| Package | Version | Dev File | Prod File |
|---------|---------|----------|-----------|
| Vue 3 | 3.5.x | `vue.esm-browser.js` | `vue.esm-browser.prod.js` |
| Pinia | 3.0.x | `pinia.esm-browser.js` | (no separate prod build) |
| Vue Router | 5.0.x | `vue-router.esm-browser.js` | `vue-router.esm-browser.prod.js` |

**Why committed to git:** These are small (~900KB total for dev builds), pinned to specific versions, and rarely change. Committing them eliminates CDN dependencies in production and makes builds fully reproducible.

**Download source:** `https://unpkg.com/<package>@<version>/dist/<filename>`

A `scripts/download-vendor.sh` script will automate downloading pinned versions.

---

## Import Map Strategy

The import map in `backend/public/index.html` maps bare specifiers to vendor files:

```html
<script type="importmap">
{
  "imports": {
    "vue": "/js/vendor/vue.esm-browser.js",
    "pinia": "/js/vendor/pinia.esm-browser.js",
    "vue-router": "/js/vendor/vue-router.esm-browser.js"
  }
}
</script>
<script type="module" src="/js/app/main.js"></script>
```

This is the key mechanism that makes the no-bundler approach work:

1. **TypeScript source** writes `import { ref } from 'vue'` — a bare specifier
2. **tsc** resolves types via `paths` in `tsconfig.json` (pointing to `node_modules/vue`)
3. **tsc output** preserves the bare specifier `from 'vue'` unchanged in the `.js` output
4. **Browser** resolves `'vue'` via the import map to `/js/vendor/vue.esm-browser.js`

Cross-vendor imports (Pinia imports from `'vue'`, Vue Router imports from `'vue'`) are also resolved by the same import map.

### Relative imports

For project-internal imports, TypeScript source uses `.js` extensions:

```typescript
// In frontend/src/main.ts
import App from './App.js'
import { router } from './router.js'
```

This is required because browsers resolve ES module imports literally. tsc with `moduleResolution: "bundler"` allows `.js` extensions in `.ts` source files and resolves them correctly during type checking.

---

## TypeScript Configuration

`frontend/tsconfig.json`:

```jsonc
{
  "compilerOptions": {
    // Output
    "outDir": "../backend/public/js/app",
    "rootDir": "src",
    "sourceMap": true,

    // Module system
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "bundler",
    "verbatimModuleSyntax": true,

    // Type checking
    "strict": true,
    "noEmit": false,
    "declaration": false,

    // Import map alignment — tsc resolves types, browser resolves runtime
    "paths": {
      "vue": ["./node_modules/vue/dist/vue.d.ts"],
      "pinia": ["./node_modules/pinia/dist/pinia.d.ts"],
      "vue-router": ["./node_modules/vue-router/dist/vue-router.d.ts"]
    },

    // Needed for Vue type support
    "jsx": "preserve",
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*.ts"]
}
```

Key settings:
- **`moduleResolution: "bundler"`** — allows `.js` extensions in imports and `paths` mapping for bare specifiers
- **`paths`** — maps bare specifiers to type declarations for type checking
- **`outDir`** — writes compiled `.js` directly to `backend/public/js/app/`
- **`verbatimModuleSyntax`** — preserves import/export syntax exactly (no CommonJS transform)
- **`target: "ES2022"`** — modern browsers only, no downlevel transforms needed

---

## Component Authoring Pattern

No SFCs (`.vue` files) — components use `defineComponent()` with template strings:

```typescript
import { defineComponent, ref, computed } from 'vue'

export default defineComponent({
  name: 'EquipmentCard',

  props: {
    name: { type: String, required: true },
    status: { type: String, required: true },
  },

  setup(props) {
    const isUp = computed(() => props.status === 'UP')
    const statusClass = computed(() => `status-${props.status.toLowerCase()}`)

    return { isUp, statusClass }
  },

  template: `
    <div class="glass-panel equipment-card">
      <h3>{{ name }}</h3>
      <span :class="statusClass">{{ status }}</span>
    </div>
  `,
})
```

**Why `defineComponent()` instead of `<script setup>`:**
- `<script setup>` is SFC syntax — requires a compiler (Vite/Vue CLI) to transform
- `defineComponent()` works with plain `.ts` files and Vue's runtime template compiler
- The full Vue ESM browser build (`vue.esm-browser.js`) includes the template compiler

**Template strings vs render functions:**
- Template strings are more readable and familiar to Vue developers
- The runtime template compiler handles them at component mount time
- Render functions (`h()`) are available as an alternative but not required

---

## Build Workflow

### npm scripts (`frontend/package.json`)

```json
{
  "scripts": {
    "typecheck": "tsc --noEmit",
    "build": "tsc",
    "watch": "tsc --watch",
    "clean": "rm -rf ../backend/public/js/app"
  }
}
```

### Development flow

1. `cd frontend && npm run watch` — tsc watches `.ts` files, transpiles on change
2. Genie.jl serves `backend/public/` as static files
3. Browser loads `index.html` → import map → ES modules
4. Manual browser refresh (no HMR)

### CI/Production flow

1. `cd frontend && npm ci` — install dev deps
2. `cd frontend && npm run typecheck` — validate types
3. `cd frontend && npm run build` — transpile .ts → .js
4. Deploy `backend/` directory (includes `public/` with vendor libs and compiled app)
5. No Node.js needed at runtime — Genie.jl serves everything

---

## Vendor Library Management

### Download script (`scripts/download-vendor.sh`)

Downloads pinned versions of vendor ESM browser builds:

```bash
#!/usr/bin/env bash
set -euo pipefail

VENDOR_DIR="backend/public/js/vendor"
mkdir -p "$VENDOR_DIR"

# Vue 3
VUE_VERSION="3.5.28"
curl -sL "https://unpkg.com/vue@${VUE_VERSION}/dist/vue.esm-browser.js" \
  -o "$VENDOR_DIR/vue.esm-browser.js"
curl -sL "https://unpkg.com/vue@${VUE_VERSION}/dist/vue.esm-browser.prod.js" \
  -o "$VENDOR_DIR/vue.esm-browser.prod.js"

# Pinia
PINIA_VERSION="3.0.4"
curl -sL "https://unpkg.com/pinia@${PINIA_VERSION}/dist/pinia.esm-browser.js" \
  -o "$VENDOR_DIR/pinia.esm-browser.js"

# Vue Router
ROUTER_VERSION="5.0.2"
curl -sL "https://unpkg.com/vue-router@${ROUTER_VERSION}/dist/vue-router.esm-browser.js" \
  -o "$VENDOR_DIR/vue-router.esm-browser.js"
curl -sL "https://unpkg.com/vue-router@${ROUTER_VERSION}/dist/vue-router.esm-browser.prod.js" \
  -o "$VENDOR_DIR/vue-router.esm-browser.prod.js"

echo "Vendor libs downloaded to $VENDOR_DIR"
ls -lh "$VENDOR_DIR"
```

### Updating vendor versions

1. Edit version numbers in `scripts/download-vendor.sh`
2. Run the script
3. Test the app in browser
4. Commit the updated vendor files

---

## index.html Entry Point

`backend/public/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>QCI Fab UI</title>
  <link rel="stylesheet" href="/css/quantum-theme.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
  <div id="app"></div>

  <script type="importmap">
  {
    "imports": {
      "vue": "/js/vendor/vue.esm-browser.js",
      "pinia": "/js/vendor/pinia.esm-browser.js",
      "vue-router": "/js/vendor/vue-router.esm-browser.js"
    }
  }
  </script>
  <script type="module" src="/js/app/main.js"></script>
</body>
</html>
```

---

## .gitignore Additions

```gitignore
# tsc output (rebuild from frontend/src/)
backend/public/js/app/

# Source maps
*.js.map
```

Note: `backend/public/js/vendor/` is NOT gitignored — vendor files are committed.

---

## Key Design Decisions

| Decision | Choice | Reasoning |
|----------|--------|-----------|
| SFC vs defineComponent | `defineComponent()` + template strings | No bundler to compile .vue files |
| vue-tsc vs tsc | Plain `tsc` | vue-tsc's value is SFC template checking; we have no SFCs |
| Compiled .js output | Gitignored | Deterministic build artifact; .ts is source of truth |
| Vendor libs | Committed to git | Small, pinned, rarely change; no CDN dependency in prod |
| CSS approach | Separate .css files | Extract from existing design reference; components use class names |
| Import resolution | Browser import maps | Bridges tsc paths and browser module loading seamlessly |
| Relative imports | `.js` extension required | Browser needs it; tsc with bundler resolution handles it |
| HMR | None (manual refresh) | No bundler means no HMR; acceptable for this project |
| Prod vs dev vendor builds | Import map swap | Change import map paths to `.prod.js` for production |

---

## Browser Compatibility

Import maps are supported in all modern browsers:
- Chrome 89+, Firefox 108+, Safari 16.4+, Edge 89+

This is an internal tool for QCI operators — modern browser requirement is acceptable.

---

## Deferred Decisions

These will be resolved during Layer 3 implementation:

- **Prod/dev import map switching:** Possibly via Genie.jl template rendering (inject different import map based on `APP_ENV`)
- **CSS extraction strategy:** How much of `index.html` design reference to extract vs rewrite
- **Testing framework:** Vitest (runs on Node, dev-only) or browser-native testing
- **Type declaration specifics:** Exact `@types/*` packages needed beyond vue/pinia/vue-router
