<template>
  <div class="ts-bar" role="region" aria-label="Accessibility options">
    <div class="ts-inner">
      <div class="ts-control" role="group" aria-label="Adjust text size">
        <span class="ts-a-small" aria-hidden="true">A</span>
        <input
          type="range"
          class="ts-slider"
          min="90"
          max="140"
          step="5"
          v-model.number="ui.textScale"
          aria-label="Text size"
          :aria-valuenow="ui.textScale"
          :aria-valuetext="`Text size ${ui.textScale}%`"
        />
        <span class="ts-a-large" aria-hidden="true">A</span>
        <span class="ts-pct" aria-hidden="true">{{ ui.textScale }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { uiStore as ui } from '../stores/uiStore'
</script>

<style scoped>
.ts-bar {
  position: fixed; top: 78px; right: 0; left: 0; z-index: 95;
  background: rgba(255,255,255,0.92); backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(29,113,105,0.08);
  box-shadow: 0 4px 16px rgba(0,0,0,0.04);
}
.ts-inner { display: flex; align-items: center; justify-content: flex-end; padding: 8px 52px; }
.ts-control {
  display: inline-flex; align-items: center; gap: 12px;
  background: rgba(255,255,255,0.9);
  border: 1.5px solid rgba(29,113,105,0.18);
  border-radius: 999px; padding: 6px 16px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.06);
}
.ts-a-small { font-family: Georgia,serif; font-size: 12px; font-weight: 700; color: #0a9b8a; line-height: 1; }
.ts-a-large { font-family: Georgia,serif; font-size: 19px; font-weight: 700; color: #0a9b8a; line-height: 1; }
.ts-slider { -webkit-appearance: none; appearance: none; width: 110px; height: 4px; background: #d1e8d4; border-radius: 999px; outline: none; cursor: pointer; }
.ts-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 18px; height: 18px; border-radius: 50%; background: #0a9b8a; box-shadow: 0 2px 8px rgba(10,155,138,0.4); cursor: pointer; transition: transform 0.2s; }
.ts-slider::-webkit-slider-thumb:hover { transform: scale(1.15); }
.ts-slider:focus-visible { outline: 3px solid #0a9b8a; outline-offset: 3px; }
.ts-pct { font-size: 12px; font-weight: 700; color: #6a8e6e; min-width: 34px; }

@media (max-width: 1000px) {
  .ts-inner { padding: 8px 20px; }
  .ts-slider { width: 90px; }
}
</style>