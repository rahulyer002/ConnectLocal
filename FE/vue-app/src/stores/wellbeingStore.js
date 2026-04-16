import { reactive } from 'vue'

export const wellbeingStore = reactive({
  hasResult: false,
  totalScore: 0,
  resultBand: '',
  resultExplanation: '',
  dimensionScores: {
    companionship: 0,
    socialConnection: 0,
    intimacy: 0
  }
})