import { ref } from 'vue'
const detectedLocationText = ref('Location not available')
export const useLocationState = () => ({
  detectedLocationText,
  setDetectedLocation: t => detectedLocationText.value = (t || '').trim() || 'Location not available',
  setDetectedUnavailable: () => detectedLocationText.value = 'Location not available',
})
