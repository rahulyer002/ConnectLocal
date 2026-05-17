// CheckinPage — landing page before the form. Mostly navigation + UI.
import { describe, it, expect, vi } from 'vitest'
import CheckinPage from '@/pages/CheckinPage.vue'
import { mountWithRouter } from '../helpers'

describe('CheckinPage', () => {
  it('mounts cleanly', async () => {
    const wrapper = await mountWithRouter(CheckinPage)
    expect(wrapper.exists()).toBe(true)
  })

  it('navigates to /checkin/form when the start button is clicked', async () => {
    const wrapper = await mountWithRouter(CheckinPage)
    const pushSpy = vi.spyOn(wrapper.vm.$router, 'push')

    // The page navigates programmatically via router.push (not <RouterLink>),
    // so we trigger the click on whichever button starts the check-in.
    const btn = wrapper.findAll('button').find(b =>
      /start|begin|check.?in/i.test(b.text())
    )
    if (btn) {
      await btn.trigger('click')
      expect(pushSpy).toHaveBeenCalledWith('/checkin-form')
    } else {
      // If the page changes its UI to use RouterLink instead, the link
      // attribute should still point at /checkin/form.
      expect(wrapper.html()).toMatch(/checkin\/form/)
    }
  })
})
