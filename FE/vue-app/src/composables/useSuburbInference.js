// useSuburbInference.js — domain wrapper for /api/inference/* endpoints.
//
// Two entry points:
//   useSuburbInference(suburbId)   — full inference payload for one suburb
//   useSuburbRankings(opts)        — top-N suburbs by a metric
//
// Both return the same {data, error, isLoading, run, abort} shape from useApi.

import { useApi, jsonFetcher } from './useApi'

const BASE = import.meta.env.VITE_API_BASE_URL
  || import.meta.env.VITE_ACTIVITIES_API_URL
  || 'https://connectlocal.duckdns.org'

export function useSuburbInference(suburbIdRef) {
  return useApi(async (signal) => {
    const id = typeof suburbIdRef === 'function' ? suburbIdRef() : suburbIdRef?.value ?? suburbIdRef
    if (id == null) throw new Error('No suburb id')
    return jsonFetcher(`${BASE}/api/inference/${id}`, { signal })
  }, { autoRetry: 1, timeoutMs: 10_000 })
}

export function useSuburbRankings(optsRef) {
  return useApi(async (signal) => {
    const opts = typeof optsRef === 'function' ? optsRef() : optsRef?.value ?? optsRef ?? {}
    const params = new URLSearchParams()
    if (opts.metric)  params.set('metric',  opts.metric)
    if (opts.persona) params.set('persona', opts.persona)
    if (opts.top)     params.set('top',     String(opts.top))
    return jsonFetcher(`${BASE}/api/inference/rankings?${params.toString()}`, { signal })
  }, { autoRetry: 1, timeoutMs: 8_000 })
}

export function useInferenceHealth() {
  return useApi(async (signal) => {
    return jsonFetcher(`${BASE}/api/inference/health`, { signal })
  }, { autoRetry: 0, timeoutMs: 5_000 })
}
