// Tests for useApi composable.
// Place this at FE/vue-app/tests/composables/useApi.spec.js
// Then run:  npm test

import { describe, it, expect, vi, afterEach } from 'vitest'
import { useApi, jsonFetcher } from '../../src/composables/useApi'

describe('useApi', () => {
  afterEach(() => { vi.useRealTimers() })

  it('sets data and clears loading on success', async () => {
    const fetcher = vi.fn(async () => ({ ok: 1 }))
    const { data, error, isLoading, run } = useApi(fetcher)
    const p = run()
    expect(isLoading.value).toBe(true)
    await p
    expect(data.value).toEqual({ ok: 1 })
    expect(error.value).toBeNull()
    expect(isLoading.value).toBe(false)
  })

  it('classifies a 404 as not-retryable with friendly copy', async () => {
    const fetcher = async () => {
      const err = new Error('HTTP 404')
      err.response = { status: 404, detail: 'Suburb 9 not found.' }
      throw err
    }
    const { error, run } = useApi(fetcher, { autoRetry: 2, retryDelay: 0 })
    await run()
    expect(error.value.kind).toBe('http')
    expect(error.value.status).toBe(404)
    expect(error.value.retryable).toBe(false)
    expect(error.value.message).toMatch(/couldn't find/i)
  })

  it('classifies a 503 as retryable and surfaces the detail message', async () => {
    let calls = 0
    const fetcher = async () => {
      calls++
      const err = new Error('HTTP 503')
      err.response = { status: 503, detail: 'Score data is being prepared. Try again.' }
      throw err
    }
    const { error, run } = useApi(fetcher, { autoRetry: 1, retryDelay: 0 })
    await run()
    expect(calls).toBe(2)
    expect(error.value.status).toBe(503)
    expect(error.value.message).toMatch(/being prepared/i)
    expect(error.value.retryable).toBe(true)
  })

  it('classifies a network failure as retryable', async () => {
    const fetcher = async () => { throw new TypeError('Failed to fetch') }
    const { error, run } = useApi(fetcher, { autoRetry: 0 })
    await run()
    expect(error.value.kind).toBe('network')
    expect(error.value.retryable).toBe(true)
  })

  it('times out and marks the error retryable', async () => {
    vi.useFakeTimers()
    const fetcher = () => new Promise(() => {})
    const { error, run } = useApi(fetcher, { timeoutMs: 50, autoRetry: 0 })
    const p = run()
    await vi.advanceTimersByTimeAsync(100)
    await p
    expect(error.value.kind).toBe('timeout')
    expect(error.value.retryable).toBe(true)
  })

  it('retries a 500 the right number of times then surfaces it', async () => {
    let calls = 0
    const fetcher = async () => {
      calls++
      const err = new Error('HTTP 500')
      err.response = { status: 500 }
      throw err
    }
    const { error, run } = useApi(fetcher, { autoRetry: 2, retryDelay: 0 })
    await run()
    expect(calls).toBe(3)
    expect(error.value.status).toBe(500)
  })
})

describe('jsonFetcher', () => {
  it('returns json on 200', async () => {
    global.fetch = vi.fn(async () => ({
      ok: true, status: 200,
      json: async () => ({ hi: 1 }),
    }))
    const result = await jsonFetcher('/x')
    expect(result).toEqual({ hi: 1 })
  })

  it('throws with response attached on non-200', async () => {
    global.fetch = vi.fn(async () => ({
      ok: false, status: 503,
      json: async () => ({ detail: 'not ready' }),
    }))
    await expect(jsonFetcher('/x')).rejects.toMatchObject({
      response: { status: 503, detail: 'not ready' },
    })
  })
})