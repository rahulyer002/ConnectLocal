// Unit tests for pure utility functions in useJourneyApi.
// These are easy, deterministic, and shouldn't need any mocking.
import { describe, it, expect } from 'vitest'
import { decodePolyline, extractPath } from '@/composables/useJourneyApi'

describe('decodePolyline', () => {
  it('returns an empty array for falsy input', () => {
    expect(decodePolyline('')).toEqual([])
    expect(decodePolyline(null)).toEqual([])
    expect(decodePolyline(undefined)).toEqual([])
  })

  it('decodes a known Google polyline into ordered lat/lng points', () => {
    // Reference value from Google's polyline algorithm docs.
    // "_p~iF~ps|U" decodes to [38.5, -120.2]
    const points = decodePolyline('_p~iF~ps|U')
    expect(points.length).toBe(1)
    expect(points[0].lat).toBeCloseTo(38.5, 4)
    expect(points[0].lng).toBeCloseTo(-120.2, 4)
  })
})

describe('extractPath', () => {
  it('returns an empty array for missing input', () => {
    expect(extractPath(null)).toEqual([])
    expect(extractPath({})).toEqual([])
  })

  it('extracts coordinates from a {lat,lng} array shape', () => {
    const result = extractPath({
      coords: [
        { lat: -37.8,  lng: 144.97 },
        { lat: -37.81, lng: 144.96 },
      ],
    })
    expect(result.length).toBe(2)
    expect(result[0]).toEqual({ lat: -37.8, lng: 144.97 })
  })

  it('extracts coordinates from a [[lat,lng], …] tuple shape', () => {
    const result = extractPath({
      points: [[-37.8, 144.97], [-37.81, 144.96]],
    })
    expect(result.length).toBe(2)
    expect(result[1].lng).toBe(144.96)
  })
})
