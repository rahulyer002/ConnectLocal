<template>
  <div class="shell">
    <aside class="side">
      <h1><span>Connect</span>Local</h1>
      <p>{{ detectedLocationText }}</p>
      <nav>
        <RouterLink to="/checkin" class="item">Wellbeing Check</RouterLink>
        <RouterLink to="/discover" class="item">Discover Events</RouterLink>
      </nav>
      <label class="scale">Text size: {{ Math.round(scale * 100) }}%
        <input type="range" min="0.75" max="1.25" step="0.05" v-model.number="scale" />
      </label>
      <section class="score"><small>WELLBEING SCORE</small><b>48</b><span>out of 80</span></section>
    </aside>
    <main>
      <nav v-if="route.path !== '/discover'" class="tabs">
        <RouterLink to="/checkin">Check-in</RouterLink>
        <RouterLink to="/results">Results</RouterLink>
        <RouterLink to="/discover">Discover</RouterLink>
      </nav>
      <slot />
    </main>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useLocationState } from '../composables/useLocationState'
const route = useRoute()
const { detectedLocationText } = useLocationState()
const scale = ref(1)
watch(scale, v => document.documentElement.style.setProperty('--font-scale', v), { immediate: true })
</script>

<style scoped>
.shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: var(--sidebar-width)1fr;
  background: var(--panel)
}

.side {
  padding: 20px;
  background: #d8d9e3;
  border-right: 1px solid var(--line);
  display: flex;
  flex-direction: column;
  gap: 12px
}

h1 {
  margin: 0;
  font: 700 calc(32px*var(--font-scale))/1 'Fraunces', serif
}

h1 span {
  color: #f56a48
}

p {
  margin: 0;
  color: var(--muted);
  font-weight: 700
}

.item {
  display: block;
  padding: 10px 8px;
  border-radius: 10px;
  font-weight: 700
}

.item.router-link-exact-active {
  background: #efdfe3
}

.scale {
  display: grid;
  gap: 6px;
  padding: 10px;
  border: 1px solid #d2d4e2;
  border-radius: 10px;
  background: #edf0f8;
  font-size: calc(13px*var(--font-scale));
  font-weight: 700
}

.score {
  margin-top: auto;
  padding: 14px;
  border: 1px solid #d8d8e8;
  border-radius: 12px;
  background: #f2f2f7;
  display: grid;
  gap: 4px
}

.score b {
  font: 700 calc(46px*var(--font-scale))/1 'Fraunces', serif;
  color: #e0a700
}

main {
  min-width: 0;
  background: #f5f5fa
}

.tabs {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border-bottom: 1px solid var(--line);
  background: #fff
}

.tabs a {
  text-align: center;
  padding: 12px;
  font-weight: 700
}

.tabs .router-link-exact-active {
  color: #f26648;
  border-bottom: 3px solid #f26648
}

@media (max-width:980px) {
  .shell {
    grid-template-columns: 1fr
  }

  .score {
    display: none
  }
}
</style>
