// useApi.js — resilient fetch wrapper with loading/error/retry/timeout.
//
// Used by all domain composables. Returns reactive refs so templates can
// render skeleton/error/empty/content branches cleanly via <AsyncState>.
//
//   const { data, error, isLoading, isStale, run, abort } =
//     useApi(() => fetch(url).then(r => r.json()), { autoRetry: 1 })
//
//   onMounted(run)
//
// Errors are normalised to a single shape regardless of cause:
//   { kind, status, message, retryable }
//     kind:      'network' | 'timeout' | 'http' | 'parse' | 'aborted'
//     status:    HTTP status code if kind === 'http', else null
//     message:   user-safe plain-English string
//     retryable: whether a retry might succeed (false for 4xx, true for 5xx + network)
//
// The fetcher you pass is responsible for building the URL and parsing JSON.
// It should THROW on a non-OK response with the response attached as
// err.response — useApi inspects err.response.status to classify HTTP errors.

import { ref, computed } from 'vue'

const DEFAULT_TIMEOUT_MS = 12_000
const DEFAULT_RETRY_DELAY_MS = 800

function classifyError(err) {
  if (err?.name === 'AbortError' || err?.kind === 'aborted') {
    return { kind: 'aborted', status: null, message: 'Request was cancelled.', retryable: false }
  }
  if (err?.kind === 'timeout') {
    return {
      kind: 'timeout', status: null,
      message: 'This is taking longer than usual. Please check your internet and try again.',
      retryable: true,
    }
  }
  const status = err?.response?.status ?? err?.status ?? null
  if (status) {
    if (status === 404) {
      return { kind: 'http', status, message: "We couldn't find what you were looking for.", retryable: false }
    }
    if (status === 503) {
      return {
        kind: 'http', status,
        message: err?.response?.detail
          || 'This information is being prepared. Please try again in a moment.',
        retryable: true,
      }
    }
    if (status >= 400 && status < 500) {
      return {
        kind: 'http', status,
        message: err?.response?.detail || 'Something about that request was invalid.',
        retryable: false,
      }
    }
    if (status >= 500) {
      return {
        kind: 'http', status,
        message: 'Our service is having a moment. Please try again shortly.',
        retryable: true,
      }
    }
  }
  if (err?.message?.includes('Failed to fetch') || err?.message?.includes('NetworkError')) {
    return {
      kind: 'network', status: null,
      message: 'We couldn\'t reach the service. Please check your internet connection.',
      retryable: true,
    }
  }
  if (err instanceof SyntaxError) {
    return { kind: 'parse', status: null, message: 'We got an unexpected response from the server.', retryable: true }
  }
  return { kind: 'network', status: null, message: 'Something went wrong. Please try again.', retryable: true }
}

export function useApi(fetcher, options = {}) {
  const {
    timeoutMs   = DEFAULT_TIMEOUT_MS,
    autoRetry   = 0,
    retryDelay  = DEFAULT_RETRY_DELAY_MS,
    onSuccess   = null,
    onError     = null,
  } = options

  const data       = ref(null)
  const error      = ref(null)
  const isLoading  = ref(false)
  const lastLoaded = ref(null)
  let controller   = null

  const isStale = computed(() => {
    if (!lastLoaded.value) return false
    return Date.now() - lastLoaded.value > 60_000
  })

  function abort() {
    if (controller) {
      controller.abort()
      controller = null
    }
    isLoading.value = false
  }

  async function attempt(signal) {
    let timeoutId
    const timeoutPromise = new Promise((_, reject) => {
      timeoutId = setTimeout(() => reject({ kind: 'timeout' }), timeoutMs)
    })
    try {
      const result = await Promise.race([fetcher(signal), timeoutPromise])
      clearTimeout(timeoutId)
      return result
    } catch (e) {
      clearTimeout(timeoutId)
      throw e
    }
  }

  async function run(...args) {
    abort()
    controller = new AbortController()
    const localController = controller
    error.value = null
    isLoading.value = true

    let attemptsLeft = autoRetry
    while (true) {
      try {
        const result = await attempt(localController.signal)
        if (localController.signal.aborted) return
        data.value = result
        lastLoaded.value = Date.now()
        isLoading.value = false
        if (onSuccess) onSuccess(result)
        return result
      } catch (rawErr) {
        if (localController.signal.aborted) {
          isLoading.value = false
          return
        }
        const classified = classifyError(rawErr)
        if (classified.retryable && attemptsLeft > 0) {
          attemptsLeft -= 1
          await new Promise(r => setTimeout(r, retryDelay))
          continue
        }
        error.value = classified
        isLoading.value = false
        if (onError) onError(classified)
        return
      }
    }
  }

  return { data, error, isLoading, isStale, run, abort, lastLoaded }
}

export async function jsonFetcher(url, init = {}) {
  const res = await fetch(url, init)
  if (!res.ok) {
    let detail = null
    try { detail = (await res.json())?.detail } catch {}
    const err = new Error(`HTTP ${res.status}`)
    err.response = { status: res.status, detail }
    err.status = res.status
    throw err
  }
  return res.json()
}
