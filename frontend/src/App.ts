import { defineComponent } from 'vue'
import QuantumBackground from './components/QuantumBackground.js'
import DockNav from './components/DockNav.js'
import LogoutButton from './components/LogoutButton.js'

export default defineComponent({
  name: 'App',

  components: {
    QuantumBackground,
    DockNav,
    LogoutButton,
  },

  template: `
    <QuantumBackground />
    <router-view />
    <DockNav />
    <LogoutButton />
  `,
})
