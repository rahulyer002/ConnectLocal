import { reactive } from 'vue'

export const resonanceStore = reactive({
  // Location (shared across all Best Time pages)
  userLat: null,
  userLon: null,
  locationLabel: '',
  locationReady: false,

  // API results
  scoreResult: null,
  safetyConditions: null,
  bestTimesResult: null,
  goNowResult: null,
  forecastResult: null,
  greenSpaces: [],
  nearbyToilets: [],
  nearbyStops: [],
  welcomingSpaces: [],

  // Loading flags
  loadingScore: false,
  loadingGoNow: false,
  loadingForecast: false,
  loadingSpaces: false,
  loadingWelcoming: false,
  error: null,

  setLocation(lat, lon, label) {
    this.userLat = lat
    this.userLon = lon
    this.locationLabel = label || `${lat.toFixed(4)}, ${lon.toFixed(4)}`
    this.locationReady = true
    // Clear stale results so pages refetch
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
    this.locationLabel = ''
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