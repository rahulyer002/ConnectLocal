import { reactive, watch } from 'vue'

const STORAGE_KEY = 'connectlocal-ui-text-scale'

const stored = (() => {
  try {
    const v = localStorage.getItem(STORAGE_KEY)
    if (v) {
      const n = parseInt(v, 10)
      if (n >= 90 && n <= 140) return n
    }
  } catch {}
  return 100
})()

export const uiStore = reactive({
  textScale: stored,
})

function applyScale(v) {
  if (typeof document !== 'undefined') {
    document.documentElement.style.setProperty('--text-scale', v / 100)
  }
}

applyScale(uiStore.textScale)

watch(() => uiStore.textScale, (v) => {
  applyScale(v)
  try { localStorage.setItem(STORAGE_KEY, String(v)) } catch {}
})