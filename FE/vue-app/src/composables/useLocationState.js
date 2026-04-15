import { ref } from 'vue'

const detectedLocationText = ref('Location not available')

const setDetectedLocation = (text) => {
  const safeText = text?.trim()
  detectedLocationText.value = safeText || 'Location not available'
}

const setDetectedUnavailable = () => {
  detectedLocationText.value = 'Location not available'
}

export const useLocationState = () => ({
  detectedLocationText,
  setDetectedLocation,
  setDetectedUnavailable,
})
