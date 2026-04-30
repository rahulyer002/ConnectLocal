<template>
  <div class="shell">
    <aside class="side">
      <RouterLink to="/home" class="logo-link">
        <h1><span>Connect</span>Local</h1>
      </RouterLink>

      <p class="location-text">{{ detectedLocationText }}</p>

      <nav>
        <RouterLink to="/home" class="item home-btn">Home Page</RouterLink>
        <RouterLink to="/checkin" class="item">Wellbeing Check</RouterLink>
        <RouterLink to="/discover" class="item">Discover Events</RouterLink>
      </nav>

      <label class="scale">
        Text size: {{ Math.round(scale * 100) }}%
        <input
          type="range"
          min="0.75"
          max="1.25"
          step="0.05"
          v-model.number="scale"
        />
      </label>
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

watch(
  scale,
  (value) => {
    document.documentElement.style.setProperty('--font-scale', value)
  },
  { immediate: true }
)
</script>

<style scoped>
.shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: var(--sidebar-width) 1fr;
  background: var(--panel);
}

.side {
  padding: 20px;
  background: #d8d9e3;
  border-right: 1px solid var(--line);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.logo-link {
  text-decoration: none;
}

h1 {
  margin: 0;
  font-family: 'Fraunces', serif;
  font-size: calc(32px * var(--font-scale));
  line-height: 1;
  font-weight: 700;
  color: #2f3152;
}

h1 span {
  color: #0c8b7d;
}

.location-text {
  margin: 0;
  color: var(--muted);
  font-size: calc(16px * var(--font-scale));
  font-weight: 700;
}

.item {
  display: block;
  padding: 10px 8px;
  border-radius: 10px;
  font-size: calc(16px * var(--font-scale));
  font-weight: 700;
}

.item.router-link-exact-active {
  background: #e3faf5;
}

.scale {
  display: grid;
  gap: 6px;
  padding: 10px;
  border: 1px solid #d2d4e2;
  border-radius: 10px;
  background: #edf0f8;
  font-size: calc(14px * var(--font-scale));
  font-weight: 700;
}

.scale input {
  width: 100%;
}

main {
  min-width: 0;
  background: #f5f5fa;
}

.tabs {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border-bottom: 1px solid var(--line);
  background: #fff;
}

.tabs a {
  text-align: center;
  padding: 12px;
  font-size: calc(16px * var(--font-scale));
  font-weight: 700;
}

.tabs .router-link-exact-active {
  color: #0c8b7d;
  border-bottom: 3px solid #0c8b7d;
}

@media (max-width: 980px) {
  .shell {
    grid-template-columns: 1fr;
  }
}


</style>