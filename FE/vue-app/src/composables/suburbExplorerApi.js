const API_BASE = "https://connectlocal.duckdns.org"

async function requestJson(url, errorMessage) {
  const response = await fetch(url)

  if (!response.ok) {
    throw new Error(errorMessage)
  }

  return response.json()
}

export function fetchSuburbMap() {
  return requestJson(
    `${API_BASE}/api/suburbs/map`,
    "Failed to load suburb map data"
  )
}

export function fetchSuburbSnapshot(suburbId) {
  return requestJson(
    `${API_BASE}/api/suburbs/${suburbId}/snapshot`,
    "Failed to load suburb snapshot"
  )
}

export function fetchSuburbPedestrian(suburbId) {
  return requestJson(
    `${API_BASE}/api/suburbs/${suburbId}/pedestrian`,
    "Failed to load pedestrian data"
  )
}

export function fetchSuburbWeather(suburbId) {
  return requestJson(
    `${API_BASE}/api/suburbs/${suburbId}/weather`,
    "Failed to load weather data"
  )
}

export function fetchSuburbEvents(suburbId, rows = 10) {
  return requestJson(
    `${API_BASE}/api/suburbs/${suburbId}/events?rows=${rows}`,
    "Failed to load suburb events"
  )
}

export function fetchSuburbAccessibility(suburbId, sampleLimit = 10) {
  return requestJson(
    `${API_BASE}/api/suburbs/${suburbId}/accessibility?sample_limit=${sampleLimit}`,
    "Failed to load accessibility data"
  )
}