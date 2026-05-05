// ResultsPage — reads wellbeingStore. Pure UI rendering test, no API.
import { describe, it, expect, beforeEach } from 'vitest'
import ResultsPage from '@/pages/ResultsPage.vue'
import { wellbeingStore } from '@/stores/wellbeingStore'
import { mountWithRouter } from '../helpers'

describe('ResultsPage', () => {
  beforeEach(() => {
    wellbeingStore.hasResult = false
    wellbeingStore.totalScore = 0
    wellbeingStore.dimensionScores = { companionship: 0, socialConnection: 0, intimacy: 0 }
    wellbeingStore.resultBand = ''
    wellbeingStore.resultExplanation = ''
  })

  it('mounts cleanly when no check-in has been completed', async () => {
    const wrapper = await mountWithRouter(ResultsPage)
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the result band when wellbeing data is present', async () => {
    wellbeingStore.hasResult = true
    wellbeingStore.totalScore = 42
    wellbeingStore.resultBand = 'Some distance from others'
    wellbeingStore.resultExplanation = 'Your responses suggest some distance from others.'
    wellbeingStore.dimensionScores = { companionship: 14, socialConnection: 16, intimacy: 12 }

    const wrapper = await mountWithRouter(ResultsPage)
    const html = wrapper.html()
    expect(html).toContain('Some distance from others')
  })
})
