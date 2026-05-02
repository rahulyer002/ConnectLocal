// src/stores/resonanceStore.js
import { reactive } from 'vue'

export const resonanceStore = reactive({
  // ── Location (shared across all Best Time pages) ──────────────────────────
  userLat: null,
  userLon: null,
  locationLabel: 'Detecting location…',
  locationReady: false,   // true once we have a valid lat/lon

  // ── API results ───────────────────────────────────────────────────────────
  scoreResult: null,          // /api/resonance/score
  safetyConditions: null,     // /api/safety/conditions
  bestTimesResult: null,      // /api/resonance/besttimes
  goNowResult: null,          // /api/resonance/gonow  (array of 3)
  forecastResult: null,       // /api/resonance/forecast
  greenSpaces: [],            // /api/greenspace/nearby
  nearbyToilets: [],          // /api/greenspace/toilets
  nearbyStops: [],            // /api/journey/stops/nearby
  welcomingSpaces: [],        // /api/landmarks/nearby?is_welcoming_space

  // ── Loading / error per section ───────────────────────────────────────────
  loadingScore: false,
  loadingGoNow: false,
  loadingForecast: false,
  loadingSpaces: false,
  error: null,

  // ── Helpers ───────────────────────────────────────────────────────────────
  setLocation(lat, lon, label) {
    this.userLat = lat
    this.userLon = lon
    this.locationLabel = label || `${lat.toFixed(4)}, ${lon.toFixed(4)}`
    this.locationReady = true
    // Clear old results so pages re-fetch for new location
    this.scoreResult = null
    this.safetyConditions = null
    this.bestTimesResult = null
    this.goNowResult = null
    this.forecastResult = null
    this.greenSpaces = []
    this.nearbyToilets = []
    this.nearbyStops = []
    this.welcomingSpaces = []
    this.error = null
  },

  reset() {
    this.userLat = null
    this.userLon = null
    this.locationLabel = 'Detecting location…'
    this.locationReady = false
    this.scoreResult = null
    this.safetyConditions = null
    this.bestTimesResult = null
    this.goNowResult = null
    this.forecastResult = null
    this.greenSpaces = []
    this.nearbyToilets = []
    this.nearbyStops = []
    this.welcomingSpaces = []
    this.error = null
  }
})