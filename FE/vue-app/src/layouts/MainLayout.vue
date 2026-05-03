<template>
  <div class="shell">
    <aside class="side">
      <RouterLink to="/home" class="logo-link">
        <h1><span>Connect</span>Local</h1>
      </RouterLink>

      <p class="location-text">{{ locationLabel }}</p>

      <nav>
        <RouterLink to="/home" class="item">Home</RouterLink>
        <RouterLink to="/checkin" class="item">Wellbeing Check</RouterLink>
        <RouterLink to="/discover" class="item">Discover Events</RouterLink>

        <!-- Best Time section with sub-links -->
        <div class="nav-group">
          <RouterLink
            to="/best-time"
            class="item best-time-link"
            :class="{ 'best-time-active': isOnBestTime }"
          >
            Best Time
          </RouterLink>

          <div class="sub-nav" v-if="isOnBestTime">
            <RouterLink to="/best-time" class="sub-item">Live score</RouterLink>
            <RouterLink to="/best-time/result" class="sub-item">Best spots now</RouterLink>
            <RouterLink to="/best-time/week" class="sub-item">Week forecast</RouterLink>
            <RouterLink to="/best-time/welcoming" class="sub-item">Welcoming spaces</RouterLink>
          </div>
        </div>
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

    <main><slot /></main>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useLocationState } from '../composables/useLocationState'
import { resonanceStore } from '../stores/resonanceStore'

const { detectedLocationText } = useLocationState()
const route = useRoute()

const locationLabel = computed(() =>
  resonanceStore.locationReady
    ? resonanceStore.locationLabel
    : detectedLocationText.value
)

const isOnBestTime = computed(() =>
  route.path.startsWith('/best-time')
)

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
  color: #008c7d;
}

.location-text {
  margin: 0;
  color: var(--muted);
  font-size: calc(14px * var(--font-scale));
  font-weight: 700;
  padding: 6px 8px;
  background: rgba(255,255,255,0.5);
  border-radius: 8px;
  word-break: break-word;
}

.item {
  display: block;
  padding: 10px 8px;
  border-radius: 10px;
  font-size: calc(16px * var(--font-scale));
  font-weight: 700;
  color: #1f2744;
  text-decoration: none;
}

.item:hover {
  background: #eefaf7;
}

.item.router-link-active {
  background: #e3faf5;
  color: #1f2744;
}

/* Best Time nav group */
.nav-group {
  display: flex;
  flex-direction: column;
  gap: 0;
}

/* Default Best Time style: same as normal nav item */
.best-time-link {
  margin-top: 4px;
  color: #1f2744;
  background: transparent;
  border: none;
}

/* Best Time only becomes green when current page is /best-time or /best-time/... */
.best-time-link.best-time-active {
  background: #e3faf5;
  color: #1f2744;
}

/* Sub-nav shown when on any /best-time/* route */
.sub-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: 4px;
  padding-left: 12px;
  border-left: 2px solid #b0ddd9;
}

.sub-item {
  display: block;
  padding: 7px 10px;
  border-radius: 8px;
  font-size: calc(14px * var(--font-scale));
  font-weight: 700;
  color: #3c6e68;
  text-decoration: none;
  transition: background 0.12s;
}

.sub-item:hover {
  background: #d8f5f0;
}

.sub-item.router-link-exact-active {
  background: #0c8b7d;
  color: #fff;
}

/* Text size slider */
.scale {
  display: grid;
  gap: 6px;
  padding: 10px;
  border: 1px solid #d2d4e2;
  border-radius: 10px;
  background: #edf0f8;
  font-size: calc(14px * var(--font-scale));
  font-weight: 700;
  margin-top: auto;
}

.scale input {
  width: 100%;
}

main {
  min-width: 0;
  background: #f5f5fa;
}

@media (max-width: 980px) {
  .shell {
    grid-template-columns: 1fr;
  }

  .side {
    padding: 14px 16px;
  }
}
</style>