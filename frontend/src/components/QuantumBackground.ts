import { defineComponent } from 'vue'

export default defineComponent({
  name: 'QuantumBackground',

  template: `
    <div class="quantum-bg"></div>
    <div class="quantum-particles">
      <div></div><div></div><div></div><div></div><div></div>
      <div></div><div></div><div></div><div></div><div></div>
    </div>
  `,
})
