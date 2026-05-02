<!-- src/components/LocationBar.vue -->
<template>
  <div class="location-bar">
    <div class="location-bar-inner">
      <span class="loc-icon">📍</span>

      <div class="input-wrap" ref="inputWrap">
        <input
          class="loc-input"
          v-model="query"
          type="text"
          placeholder="Enter suburb or postcode…"
          autocomplete="off"
          @input="onInput"
          @keydown.escape="closeDropdown"
          @keydown.enter="pickFirst"
          :aria-label="'Location search'"
        />

        <!-- Autocomplete dropdown -->
        <ul v-if="suggestions.length" class="suggestions">
          <li
            v-for="s in suggestions"
            :key="s.suburb_name"
            class="suggestion-item"
            @mousedown.prevent="selectSuburb(s)"
          >
            <span class="sug-name">{{ s.suburb_name }}</span>
            <span class="sug-state">VIC</span>
          </li>
        </ul>
      </div>

      <button
        class="locate-btn"
        @click="locateMe"
        :disabled="locating"
        title="Use my current location"
      >
        <span v-if="locating" class="spin">⟳</span>
        <span v-else>⊙ Locate me</span>
      </button>

      <div class="active-loc" v-if="resonanceStore.locationReady">
        <span class="loc-dot"></span>
        {{ resonanceStore.locationLabel }}
      </div>
    </div>

    <p v-if="errorMsg" class="loc-error">{{ errorMsg }}</p>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { resonanceStore } from '../stores/resonanceStore'
import { searchSuburbs } from '../composables/useResonanceApi'

const emit = defineEmits(['locationChanged'])

const query = ref('')
const suggestions = ref([])
const locating = ref(false)
const errorMsg = ref('')
let debounceTimer = null

function onInput() {
  clearTimeout(debounceTimer)
  errorMsg.value = ''
  if (query.value.trim().length < 2) {
    suggestions.value = []
    return
  }
  debounceTimer = setTimeout(async () => {
    suggestions.value = await searchSuburbs(query.value.trim())
  }, 280)
}

function selectSuburb(s) {
  query.value = s.suburb_name
  suggestions.value = []
  resonanceStore.setLocation(s.centroid_lat, s.centroid_lng, s.suburb_name)
  emit('locationChanged')
}

function pickFirst() {
  if (suggestions.value.length) selectSuburb(suggestions.value[0])
}

function closeDropdown() {
  suggestions.value = []
}

async function locateMe() {
  if (!navigator.geolocation) {
    errorMsg.value = 'Geolocation is not supported by your browser.'
    return
  }
  locating.value = true
  errorMsg.value = ''
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const { latitude, longitude } = pos.coords
      resonanceStore.setLocation(latitude, longitude, 'Your current location')
      query.value = ''
      locating.value = false
      emit('locationChanged')
    },
    () => {
      errorMsg.value = 'Could not detect location. Please type your suburb.'
      locating.value = false
    },
    { timeout: 8000 }
  )
}

// Close dropdown on outside click
function handleOutsideClick(e) {
  if (!e.target.closest('.input-wrap')) suggestions.value = []
}
if (typeof window !== 'undefined') {
  document.addEventListener('mousedown', handleOutsideClick)
}
</script>

<style scoped>
.location-bar {
  background: #fff;
  border-bottom: 1.5px solid #e0e1ed;
  padding: 12px 40px;
  position: sticky;
  top: 0;
  z-index: 50;
}

.location-bar-inner {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.loc-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.input-wrap {
  position: relative;
  flex: 1;
  min-width: 180px;
  max-width: 360px;
}

.loc-input {
  width: 100%;
  padding: 9px 14px;
  border: 1.5px solid #d0d2e4;
  border-radius: 10px;
  font-size: calc(15px * var(--font-scale));
  font-family: 'Manrope', sans-serif;
  color: #2f3152;
  background: #f8f8fc;
  outline: none;
  transition: border-color 0.15s;
}

.loc-input:focus { border-color: #0c8b7d; background: #fff; }

.suggestions {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: #fff;
  border: 1.5px solid #d0d2e4;
  border-radius: 12px;
  list-style: none;
  margin: 0;
  padding: 4px 0;
  box-shadow: 0 8px 24px rgba(0,0,0,0.10);
  z-index: 100;
}

.suggestion-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  cursor: pointer;
  transition: background 0.12s;
}

.suggestion-item:hover { background: #f0faf8; }

.sug-name {
  font-size: calc(14px * var(--font-scale));
  font-weight: 700;
  color: #2f3152;
}

.sug-state {
  font-size: calc(12px * var(--font-scale));
  color: #9b9db8;
  font-weight: 600;
}

.locate-btn {
  padding: 9px 16px;
  border: 1.5px solid #0c8b7d;
  border-radius: 10px;
  background: #fff;
  color: #0c8b7d;
  font-size: calc(14px * var(--font-scale));
  font-weight: 700;
  font-family: 'Manrope', sans-serif;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s;
}

.locate-btn:hover:not(:disabled) { background: #0c8b7d; color: #fff; }
.locate-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.spin { display: inline-block; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.active-loc {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: calc(13px * var(--font-scale));
  font-weight: 700;
  color: #0c8b7d;
  padding: 6px 12px;
  background: #e8f8f5;
  border-radius: 999px;
  white-space: nowrap;
}

.loc-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: #0c8b7d;
  flex-shrink: 0;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.loc-error {
  margin: 8px 0 0;
  font-size: calc(13px * var(--font-scale));
  color: #c84848;
  font-weight: 600;
}

@media (max-width: 900px) {
  .location-bar { padding: 12px 16px; }
  .input-wrap { max-width: 100%; }
}
</style>