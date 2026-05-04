<template>
  <div class="bt-loc-bar" ref="rootRef">
    <div class="bt-loc-inner">
      <div class="bt-loc-search-wrap">
        <svg class="bt-loc-pin" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/>
          <circle cx="12" cy="10" r="2.5"/>
        </svg>
        <input
          ref="inputRef"
          class="bt-loc-input"
          type="text"
          v-model="locationInput"
          :placeholder="store.locationReady ? store.locationLabel : 'Type a Melbourne suburb or postcode'"
          autocomplete="off"
          aria-label="Suburb or postcode"
          :aria-expanded="showSuggestions"
          aria-autocomplete="list"
          aria-controls="bt-suburb-listbox"
          @input="onInput"
          @focus="onFocus"
          @keydown="onKeyDown"
        />
        <button v-if="locationInput" class="bt-loc-clear" type="button" aria-label="Clear search" @click="clearInput">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
        <span v-if="isSearching" class="bt-loc-spin" aria-hidden="true"></span>

        <ul
          v-if="showSuggestions && (suggestions.length || noResultsHint)"
          id="bt-suburb-listbox"
          class="bt-loc-suggestions"
          role="listbox"
        >
          <li
            v-for="(s, i) in suggestions"
            :key="`${s.suburb_id}-${s.suburb_name}`"
            class="bt-loc-sugg"
            :class="{ active: i === activeIndex }"
            role="option"
            :aria-selected="i === activeIndex"
            @mouseenter="activeIndex = i"
            @mousedown.prevent="selectSuggestion(s)"
          >
            <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/>
              <circle cx="12" cy="10" r="2.5"/>
            </svg>
            <span class="bt-loc-sugg-name">{{ s.suburb_name }}</span>
            <span class="bt-loc-sugg-state">VIC</span>
          </li>
          <li v-if="!suggestions.length && noResultsHint" class="bt-loc-sugg-empty">
            No suburbs match. Try "Carlton" or use Locate me.
          </li>
        </ul>
      </div>

      <div class="bt-loc-actions">
        <button type="button" class="bt-loc-btn locate" :disabled="isLocating" @click="locateMe">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>
          </svg>
          {{ isLocating ? 'Locating…' : 'Locate me' }}
        </button>
        <button type="button" class="bt-loc-btn search" :disabled="!locationInput.trim() || isSearching" @click="submitSearch">
          Search
        </button>
      </div>

      <div v-if="store.locationReady" class="bt-loc-active">
        <span class="bt-loc-active-dot" aria-hidden="true"></span>
        <span class="bt-loc-active-text">{{ store.locationLabel }}</span>
        <button type="button" class="bt-loc-active-change" @click="focusInput" aria-label="Change location">Change</button>
      </div>
    </div>

    <p v-if="locationError" class="bt-loc-error" role="alert">{{ locationError }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { resonanceStore } from '../stores/resonanceStore'
import { searchSuburbs } from '../composables/useResonanceApi'

const store = resonanceStore

const locationInput = ref('')
const suggestions = ref([])
const showSuggestions = ref(false)
const isSearching = ref(false)
const isLocating = ref(false)
const locationError = ref('')
const activeIndex = ref(-1)
const noResultsHint = ref(false)
const rootRef = ref(null)
const inputRef = ref(null)
let debounceTimer = null

function onInput() {
  clearTimeout(debounceTimer)
  locationError.value = ''
  noResultsHint.value = false
  activeIndex.value = -1
  const q = locationInput.value.trim()
  if (q.length < 2) {
    suggestions.value = []
    showSuggestions.value = false
    return
  }
  isSearching.value = true
  debounceTimer = setTimeout(async () => {
    const results = await searchSuburbs(q, 6)
    suggestions.value = results || []
    isSearching.value = false
    showSuggestions.value = true
    noResultsHint.value = !results.length
  }, 280)
}

function onFocus() {
  if (suggestions.value.length || (locationInput.value.trim().length >= 2 && noResultsHint.value)) {
    showSuggestions.value = true
  }
}

function onKeyDown(e) {
  if (e.key === 'ArrowDown' && showSuggestions.value && suggestions.value.length) {
    e.preventDefault()
    activeIndex.value = (activeIndex.value + 1) % suggestions.value.length
  } else if (e.key === 'ArrowUp' && showSuggestions.value && suggestions.value.length) {
    e.preventDefault()
    activeIndex.value = activeIndex.value <= 0 ? suggestions.value.length - 1 : activeIndex.value - 1
  } else if (e.key === 'Enter') {
    e.preventDefault()
    if (suggestions.value.length) {
      const idx = activeIndex.value >= 0 ? activeIndex.value : 0
      selectSuggestion(suggestions.value[idx])
    } else {
      submitSearch()
    }
  } else if (e.key === 'Escape') {
    showSuggestions.value = false
    activeIndex.value = -1
  }
}

function selectSuggestion(s) {
  if (!s) return
  const lat = s.centroid_lat ?? s.lat
  const lon = s.centroid_lng ?? s.centroid_lon ?? s.lon
  if (lat == null || lon == null) {
    locationError.value = 'That suburb is missing coordinates. Try another or use Locate me.'
    return
  }
  locationInput.value = ''
  suggestions.value = []
  showSuggestions.value = false
  activeIndex.value = -1
  store.setLocation(lat, lon, s.suburb_name)
}

async function submitSearch() {
  const q = locationInput.value.trim()
  if (!q) return
  if (suggestions.value.length) {
    selectSuggestion(suggestions.value[0])
    return
  }
  isSearching.value = true
  locationError.value = ''
  const results = await searchSuburbs(q, 1)
  isSearching.value = false
  if (results.length) {
    selectSuggestion(results[0])
  } else {
    locationError.value = /^\d{4}$/.test(q)
      ? 'Postcode lookup not found. Try the suburb name (e.g. "Carlton") or use Locate me.'
      : 'No match. Check the spelling or use Locate me.'
  }
}

function clearInput() {
  locationInput.value = ''
  suggestions.value = []
  showSuggestions.value = false
  noResultsHint.value = false
  activeIndex.value = -1
  inputRef.value?.focus()
}

function focusInput() {
  inputRef.value?.focus()
  inputRef.value?.select()
}

function locateMe() {
  if (!navigator.geolocation) {
    locationError.value = 'Geolocation is not supported by your browser.'
    return
  }
  isLocating.value = true
  locationError.value = ''
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      store.setLocation(pos.coords.latitude, pos.coords.longitude, 'Your current location')
      locationInput.value = ''
      suggestions.value = []
      showSuggestions.value = false
      isLocating.value = false
    },
    () => {
      locationError.value = 'Could not detect location. Please type a suburb instead.'
      isLocating.value = false
    },
    { timeout: 8000, enableHighAccuracy: false }
  )
}

function handleOutsideClick(e) {
  if (rootRef.value && !rootRef.value.contains(e.target)) {
    showSuggestions.value = false
  }
}

onMounted(() => { document.addEventListener('mousedown', handleOutsideClick) })
onBeforeUnmount(() => {
  document.removeEventListener('mousedown', handleOutsideClick)
  clearTimeout(debounceTimer)
})
</script>

<style scoped>
.bt-loc-bar {
  position: fixed; top: 130px; left: 0; right: 0; z-index: 80;
  background: rgba(255,255,255,0.94); backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(29,113,105,0.12);
  box-shadow: 0 4px 16px rgba(0,0,0,0.04);
  padding: 10px 0;
}

.bt-loc-inner {
  max-width: 1500px; margin: 0 auto;
  display: flex; align-items: center; gap: 12px;
  padding: 0 52px;
}

.bt-loc-search-wrap {
  position: relative;
  display: flex; align-items: center; gap: 10px;
  flex: 1; min-width: 0; max-width: 540px;
  padding: 10px 14px;
  background: #f6fbf3;
  border: 1.5px solid rgba(29,113,105,0.18);
  border-radius: 12px;
  transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
}
.bt-loc-search-wrap:focus-within { border-color: #0a9b8a; background: white; box-shadow: 0 0 0 3px rgba(10,155,138,0.12); }
.bt-loc-pin { color: #0a9b8a; flex-shrink: 0; }
.bt-loc-input {
  flex: 1; min-width: 0;
  border: none; outline: none; background: transparent;
  font-family: system-ui,sans-serif; font-size: 15px; font-weight: 600; color: #1a2e1e;
}
.bt-loc-input::placeholder { color: #8aaa8e; font-weight: 500; }

.bt-loc-clear {
  display: inline-flex; align-items: center; justify-content: center;
  width: 22px; height: 22px; border-radius: 50%; border: none;
  background: rgba(29,113,105,0.1); color: #1d7169; cursor: pointer;
  transition: background 0.15s; flex-shrink: 0;
}
.bt-loc-clear:hover { background: rgba(29,113,105,0.2); }
.bt-loc-spin { width: 14px; height: 14px; border-radius: 50%; border: 2px solid rgba(10,155,138,0.25); border-top-color: #0a9b8a; animation: bt-spin 0.7s linear infinite; flex-shrink: 0; }
@keyframes bt-spin { to { transform: rotate(360deg); } }

.bt-loc-suggestions {
  position: absolute; top: calc(100% + 6px); left: 0; right: 0;
  list-style: none; margin: 0;
  background: white; border: 1.5px solid rgba(10,155,138,0.18);
  border-radius: 12px; padding: 6px;
  box-shadow: 0 16px 36px rgba(0,0,0,0.12);
  z-index: 90;
  max-height: 280px; overflow-y: auto;
}
.bt-loc-sugg {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: 8px; cursor: pointer;
  color: #0a9b8a;
  transition: background 0.12s;
}
.bt-loc-sugg:hover, .bt-loc-sugg.active { background: #e8f8f0; }
.bt-loc-sugg-name { flex: 1; font-family: system-ui,sans-serif; font-size: 14px; font-weight: 700; color: #0f1e12; }
.bt-loc-sugg-state { font-family: system-ui,sans-serif; font-size: 11px; font-weight: 700; color: #8aaa8e; letter-spacing: 0.05em; }
.bt-loc-sugg-empty { padding: 12px 14px; font-family: system-ui,sans-serif; font-size: 13px; color: #8aaa8e; font-style: italic; }

.bt-loc-actions { display: flex; gap: 8px; flex-shrink: 0; }
.bt-loc-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 9px 16px; border-radius: 10px;
  font-family: system-ui,sans-serif; font-size: 13px; font-weight: 700;
  cursor: pointer; transition: all 0.2s; border: 1.5px solid transparent;
}
.bt-loc-btn.locate { background: #f0faf0; border-color: rgba(29,113,105,0.2); color: #0a9b8a; }
.bt-loc-btn.locate:hover:not(:disabled) { background: #0a9b8a; color: white; border-color: #0a9b8a; }
.bt-loc-btn.search { background: #0a9b8a; color: white; }
.bt-loc-btn.search:hover:not(:disabled) { background: #056b5e; }
.bt-loc-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.bt-loc-active {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 6px 12px;
  background: #e8f8f0; border: 1px solid rgba(10,155,138,0.2);
  border-radius: 999px;
  flex-shrink: 0;
}
.bt-loc-active-dot { width: 7px; height: 7px; border-radius: 50%; background: #0a9b8a; animation: bt-pulse 2s ease-in-out infinite; }
@keyframes bt-pulse { 0%,100%{opacity:1} 50%{opacity:0.45} }
.bt-loc-active-text { font-family: system-ui,sans-serif; font-size: 13px; font-weight: 700; color: #0a6e62; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bt-loc-active-change { background: none; border: none; color: #0a9b8a; font-family: system-ui,sans-serif; font-size: 12px; font-weight: 700; cursor: pointer; padding: 0; text-decoration: underline; }
.bt-loc-active-change:hover { color: #056b5e; }

.bt-loc-error {
  max-width: 1500px; margin: 6px auto 0; padding: 0 52px;
  font-family: system-ui,sans-serif; font-size: 13px; color: #b3261e; font-weight: 600;
}

@media (max-width: 980px) {
  .bt-loc-inner { flex-wrap: wrap; padding: 0 20px; gap: 8px; }
  .bt-loc-search-wrap { max-width: none; flex: 1 1 100%; }
  .bt-loc-actions { flex: 1; }
  .bt-loc-btn { flex: 1; justify-content: center; }
  .bt-loc-active { width: 100%; justify-content: center; }
  .bt-loc-error { padding: 0 20px; }
}
</style>