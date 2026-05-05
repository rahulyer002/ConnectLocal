// CheckinFormPage — pure logic, no API. Tests the wellbeing scoring flow.
import { describe, it, expect, beforeEach } from 'vitest'
import CheckinFormPage from '@/pages/CheckinFormPage.vue'
import { wellbeingStore } from '@/stores/wellbeingStore'
import { mountWithRouter, flush } from '../helpers'

describe('CheckinFormPage', () => {
  beforeEach(() => {
    // Reset store before each test
    wellbeingStore.hasResult = false
    wellbeingStore.totalScore = 0
    wellbeingStore.dimensionScores = { companionship: 0, socialConnection: 0, intimacy: 0 }
  })

  it('renders question 1 of 20 on mount', async () => {
    const wrapper = await mountWithRouter(CheckinFormPage)
    expect(wrapper.text()).toMatch(/Question.*1.*of.*20/)
  })

  it('records an answer when an option button is clicked', async () => {
    const wrapper = await mountWithRouter(CheckinFormPage)
    const optionButtons = wrapper.findAll('.option-btn')
    expect(optionButtons.length).toBe(4) // Never / Rarely / Sometimes / Often
    await optionButtons[0].trigger('click')
    // After clicking, that button should show as selected
    expect(optionButtons[0].classes()).toContain('selected')
  })

  it('blocks Next button when no answer is selected (validation)', async () => {
    const wrapper = await mountWithRouter(CheckinFormPage)
    // Try to advance with nothing selected — should NOT advance past Q1
    const nextBtn = wrapper.findAll('button').find(b =>
      /next/i.test(b.text()) && !b.text().toLowerCase().includes('previous')
    )
    if (nextBtn) {
      await nextBtn.trigger('click')
      await flush()
      // Still on question 1
      expect(wrapper.text()).toMatch(/Question.*1.*of.*20/)
    }
  })
})
