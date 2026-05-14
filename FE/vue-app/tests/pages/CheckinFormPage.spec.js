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

  it('renders page 1 of 5 on mount', async () => {
    const wrapper = await mountWithRouter(CheckinFormPage)
    expect(wrapper.text()).toMatch(/Page.*1.*of.*5/)
  })

  it('records an answer when an option button is clicked', async () => {
    const wrapper = await mountWithRouter(CheckinFormPage)
    const optionButtons = wrapper.findAll('.option-btn')
    // 4 statements per page × 4 options (Never / Rarely / Sometimes / Often) = 16
    expect(optionButtons.length).toBe(16)
    // optionButtons[0] is "Never" for Statement 1 — click it and confirm selection.
    await optionButtons[0].trigger('click')
    expect(optionButtons[0].classes()).toContain('selected')
  })

  it('blocks Next button when no answer is selected (validation)', async () => {
    const wrapper = await mountWithRouter(CheckinFormPage)
    // Try to advance with nothing selected — should NOT advance past page 1.
    const nextBtn = wrapper.findAll('button').find(b =>
      /next/i.test(b.text()) && !b.text().toLowerCase().includes('previous')
    )
    if (nextBtn) {
      await nextBtn.trigger('click')
      await flush()
      // Still on page 1
      expect(wrapper.text()).toMatch(/Page.*1.*of.*5/)
      // ...and the validation message is now visible
      expect(wrapper.text()).toMatch(/Please answer all .* questions/i)
    }
  })

  it('advances to page 2 only after all 4 answers are given', async () => {
    const wrapper = await mountWithRouter(CheckinFormPage)
    const optionButtons = wrapper.findAll('.option-btn')

    // 16 buttons, ordered: [S1-Never, S1-Rarely, S1-Sometimes, S1-Often,
    //                       S2-Never, S2-Rarely, ...] — click "Never" for each.
    await optionButtons[0].trigger('click')   // S1
    await optionButtons[4].trigger('click')   // S2
    await optionButtons[8].trigger('click')   // S3
    await optionButtons[12].trigger('click')  // S4

    const nextBtn = wrapper.findAll('button').find(b =>
      /next/i.test(b.text()) && !b.text().toLowerCase().includes('previous')
    )
    await nextBtn.trigger('click')
    await flush()

    expect(wrapper.text()).toMatch(/Page.*2.*of.*5/)
  })
})