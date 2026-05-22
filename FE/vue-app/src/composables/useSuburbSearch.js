// useSuburbSearch.js — debounced suburb search.
//
// Wraps /api/suburbs/search with 250ms debounce + abort on subsequent
// keystrokes, so typing fast doesn't pile up requests.

import { ref, watch } from 'vue'
import { jsonFetcher } from './useApi'

const BASE = import.meta.env.VITE_API_BASE_URL
  || import.meta.env.VITE_ACTIVITIES_API_URL
  || 'https://connectlocal.duckdns.org'

const DEBOUNCE_MS = 250
const MIN_QUERY_CHARS = 1

export function useSuburbSearch() {
  const query     = ref('')
  const results   = ref([])
  const error     = ref(null)
  const isLoading = ref(false)

  let debounceTimer = null
  let controller    = null

  watch(query, (q) => {
    clearTimeout(debounceTimer)
    if (controller) { try { controller.abort() } catch {} }
    controller = null

    const text = (q || '').trim()
    if (text.length < MIN_QUERY_CHARS) {
      results.value = []
      error.value   = null
      isLoading.value = false
      return
    }

    isLoading.value = true
    debounceTimer = setTimeout(async () => {
      controller = new AbortController()
      try {
        const data = await jsonFetcher(
          `${BASE}/api/suburbs/search?q=${encodeURIComponent(text)}&limit=8`,
          { signal: controller.signal },
        )
        const all = data?.suburbs || []
        // Safety net: filter to prefix matches only, in case the backend
        // still does a contains-match. "carl" should match Carlton, not Macleod.
        const lowerQ = text.toLowerCase()
        results.value = all.filter((s) =>
          (s?.suburb_name || '').toLowerCase().startsWith(lowerQ)
        )
        error.value = null
      } catch (e) {
        if (e?.name !== 'AbortError') {
          error.value = "Couldn't search right now."
          results.value = []
        }
      } finally {
        isLoading.value = false
      }
    }, DEBOUNCE_MS)
  })

  function clear() {
    clearTimeout(debounceTimer)
    if (controller) { try { controller.abort() } catch {} }
    query.value     = ''
    results.value   = []
    error.value     = null
    isLoading.value = false
  }

  return { query, results, error, isLoading, clear }
}