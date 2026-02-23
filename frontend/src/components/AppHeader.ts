import { defineComponent } from 'vue'

export default defineComponent({
  name: 'AppHeader',

  setup() {
    return {}
  },

  template: `
    <header class="app-header">
      <span class="app-header__title">QCI Foundry Services</span>
    </header>
  `,
})
