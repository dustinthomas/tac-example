#!/usr/bin/env bash
set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Derive PROJECT_ROOT from script location
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"

VENDOR_DIR="$PROJECT_ROOT/backend/public/js/vendor"
mkdir -p "$VENDOR_DIR"

# Pinned versions
VUE_VERSION="3.5.28"
PINIA_VERSION="3.0.4"
ROUTER_VERSION="5.0.2"

echo -e "${BLUE}Downloading vendor ESM browser builds...${NC}"

# Vue 3
echo -e "  Vue ${VUE_VERSION} (dev)..."
curl -sL "https://unpkg.com/vue@${VUE_VERSION}/dist/vue.esm-browser.js" \
  -o "$VENDOR_DIR/vue.esm-browser.js"

echo -e "  Vue ${VUE_VERSION} (prod)..."
curl -sL "https://unpkg.com/vue@${VUE_VERSION}/dist/vue.esm-browser.prod.js" \
  -o "$VENDOR_DIR/vue.esm-browser.prod.js"

# Pinia
echo -e "  Pinia ${PINIA_VERSION}..."
curl -sL "https://unpkg.com/pinia@${PINIA_VERSION}/dist/pinia.esm-browser.js" \
  -o "$VENDOR_DIR/pinia.esm-browser.js"

# Vue Router
echo -e "  Vue Router ${ROUTER_VERSION} (dev)..."
curl -sL "https://unpkg.com/vue-router@${ROUTER_VERSION}/dist/vue-router.esm-browser.js" \
  -o "$VENDOR_DIR/vue-router.esm-browser.js"

echo -e "  Vue Router ${ROUTER_VERSION} (prod)..."
curl -sL "https://unpkg.com/vue-router@${ROUTER_VERSION}/dist/vue-router.esm-browser.prod.js" \
  -o "$VENDOR_DIR/vue-router.esm-browser.prod.js"

echo ""
echo -e "${GREEN}Vendor libs downloaded to ${VENDOR_DIR}${NC}"
ls -lh "$VENDOR_DIR"
