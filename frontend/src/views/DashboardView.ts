import { defineComponent } from 'vue'
import AppHeader from '../components/AppHeader.js'

export default defineComponent({
  name: 'DashboardView',

  components: { AppHeader },

  template: `
    <div class="main-content">
      <div class="dashboard">
        <div class="glass-panel">
          <AppHeader />
          <div class="header">
            <h1>QCI Foundry Services</h1>
            <div class="quantum-line"></div>
            <p>Fabricating photonic computing engines using thin film lithium niobate (TFLN). Our foundry enables the future of integrated photonics with accessible and affordable quantum machines.</p>
          </div>

          <div class="feature-grid">
            <div class="feature-card">
              <h3>TFLN Fabrication</h3>
              <p>State-of-the-art thin film lithium niobate processing</p>
            </div>
            <div class="feature-card">
              <h3>Photonic Engines</h3>
              <p>High-performance quantum photonic computing chips</p>
            </div>
            <div class="feature-card">
              <h3>Room Temperature</h3>
              <p>No cryogenic cooling required for operation</p>
            </div>
            <div class="feature-card">
              <h3>Scalable Production</h3>
              <p>From prototype to high-volume manufacturing</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
})
