<template>
  <MainLayout>
    <div class="checkin-page">
      <div class="noise" aria-hidden="true"></div>
      <div class="orb orb-1" aria-hidden="true"></div>
      <div class="orb orb-2" aria-hidden="true"></div>

      <header class="hero-band">
        <div class="hero-bg-word" aria-hidden="true">WELLBEING</div>
        <div class="hero-inner">
          <p class="hero-eyebrow">
            <span class="eyebrow-line" aria-hidden="true"></span>
            Your weekly wellbeing check-in
          </p>

          <h1 class="hero-headline" :style="{ fontSize: scaledPx(72) }">
            How are you feeling<br>
            <em>about your connections?</em>
          </h1>

          <p class="hero-sub" :style="{ fontSize: scaledPx(18) }">
            This gentle 5-minute check-in helps you understand how connected you feel
            to the people around you, and points you toward warm, welcoming activities
            in your neighbourhood.
          </p>

          <div
            class="progress-wrap"
            role="progressbar"
            :aria-valuenow="currentPage + 1"
            :aria-valuemin="1"
            :aria-valuemax="totalPages"
            :aria-label="`Page ${currentPage + 1} of ${totalPages}`"
          >
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
            </div>

            <span class="progress-label" :style="{ fontSize: scaledPx(14) }">
              Page <strong>{{ currentPage + 1 }}</strong> of {{ totalPages }}
            </span>
          </div>
        </div>
      </header>

      <main class="main-wrap" id="main-content">
        <div class="questions-grid">
          <div
            v-for="question in currentQuestions"
            :key="question.id"
            class="question-card"
            role="region"
            :aria-label="`Question ${question.id} of ${questions.length}`"
          >
            <p class="q-eyebrow" :style="{ fontSize: scaledPx(12) }">
              Statement {{ question.id }}
            </p>

            <h2 class="q-text" :style="{ fontSize: scaledPx(34) }">
              {{ question.text }}
            </h2>

            <div class="options" role="group" :aria-label="`Answer options for statement ${question.id}`">
              <button
                v-for="option in options"
                :key="option.value"
                class="option-btn"
                :class="{ selected: answers[question.id - 1] === option.value }"
                :aria-pressed="answers[question.id - 1] === option.value"
                @click="selectAnswer(question.id - 1, option.value)"
                :style="{ fontSize: scaledPx(17) }"
              >
                <span class="option-indicator" aria-hidden="true">
                  <svg
                    v-if="answers[question.id - 1] === option.value"
                    viewBox="0 0 24 24"
                    width="14"
                    height="14"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2.8"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path d="M20 6L9 17l-5-5"/>
                  </svg>
                </span>

                <span class="option-label">{{ option.label }}</span>
              </button>
            </div>
          </div>
        </div>

        <p
          v-if="showValidation"
          class="validation-msg"
          role="alert"
          aria-live="assertive"
          :style="{ fontSize: scaledPx(14) }"
        >
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 8v4M12 16h.01"/>
          </svg>
          Please answer all 4 questions before continuing.
        </p>

        <div class="nav-actions">
          <button
            class="btn-secondary"
            @click="goPrevious"
            :disabled="currentPage === 0"
            aria-label="Go to previous page"
            :style="{ fontSize: scaledPx(16) }"
          >
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M15 18l-6-6 6-6"/>
            </svg>
            Previous
          </button>

          <div class="dot-track" aria-hidden="true">
            <span
              v-for="(_, i) in totalPages"
              :key="i"
              class="dot"
              :class="{ active: i === currentPage, answered: isPageAnswered(i) }"
            ></span>
          </div>

          <button
            v-if="!isLastPage"
            class="btn-primary"
            @click="goNext"
            aria-label="Go to next page"
            :style="{ fontSize: scaledPx(16) }"
          >
            Next
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </button>

          <button
            v-else
            class="btn-primary btn-finish"
            @click="finishCheckIn"
            aria-label="Finish check-in and see your results"
            :style="{ fontSize: scaledPx(16) }"
          >
            See my results
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M5 12h14M13 5l7 7-7 7"/>
            </svg>
          </button>
        </div>
      </main>
    </div>
  </MainLayout>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import { wellbeingStore } from '../stores/wellbeingStore'
import { uiStore } from '../stores/uiStore'

const router = useRouter()
const scaledPx = (base) => `${(base * uiStore.textScale) / 100}px`

const options = [
  { label: 'Never', value: 1 },
  { label: 'Rarely', value: 2 },
  { label: 'Sometimes', value: 3 },
  { label: 'Often', value: 4 }
]

const questions = [
  { id: 1,  text: 'How often do you feel that you are "in tune" with the people around you?', reverse: true,  dimension: 'socialConnection' },
  { id: 2,  text: 'How often do you feel that you lack companionship?', reverse: false, dimension: 'companionship' },
  { id: 3,  text: 'How often do you feel that there is no one you can turn to?', reverse: false, dimension: 'intimacy' },
  { id: 4,  text: 'How often do you feel alone?', reverse: false, dimension: 'companionship' },
  { id: 5,  text: 'How often do you feel part of a group of friends?', reverse: true,  dimension: 'socialConnection' },
  { id: 6,  text: 'How often do you feel that you have a lot in common with the people around you?', reverse: true, dimension: 'socialConnection' },
  { id: 7,  text: 'How often do you feel that you are no longer close to anyone?', reverse: false, dimension: 'intimacy' },
  { id: 8,  text: 'How often do you feel that your interests and ideas are not shared by those around you?', reverse: false, dimension: 'socialConnection' },
  { id: 9,  text: 'How often do you feel outgoing and friendly?', reverse: true,  dimension: 'socialConnection' },
  { id: 10, text: 'How often do you feel close to people?', reverse: true,  dimension: 'intimacy' },
  { id: 11, text: 'How often do you feel left out?', reverse: false, dimension: 'socialConnection' },
  { id: 12, text: 'How often do you feel that your relationships with others are not meaningful?', reverse: false, dimension: 'intimacy' },
  { id: 13, text: 'How often do you feel that no one really knows you well?', reverse: false, dimension: 'intimacy' },
  { id: 14, text: 'How often do you feel isolated from others?', reverse: false, dimension: 'companionship' },
  { id: 15, text: 'How often do you feel you can find companionship when you want it?', reverse: true,  dimension: 'companionship' },
  { id: 16, text: 'How often do you feel that there are people who really understand you?', reverse: true,  dimension: 'intimacy' },
  { id: 17, text: 'How often do you feel shy?', reverse: false, dimension: 'socialConnection' },
  { id: 18, text: 'How often do you feel that people are around you but not with you?', reverse: false, dimension: 'companionship' },
  { id: 19, text: 'How often do you feel that there are people you can talk to?', reverse: true,  dimension: 'intimacy' },
  { id: 20, text: 'How often do you feel that there are people you can turn to?', reverse: true,  dimension: 'intimacy' }
]

const questionsPerPage = 4
const currentPage = ref(0)
const answers = ref(Array(questions.length).fill(null))
const showValidation = ref(false)

const totalPages = computed(() => Math.ceil(questions.length / questionsPerPage))
const isLastPage = computed(() => currentPage.value === totalPages.value - 1)
const progressPercent = computed(() => ((currentPage.value + 1) / totalPages.value) * 100)

const currentQuestions = computed(() => {
  const start = currentPage.value * questionsPerPage
  return questions.slice(start, start + questionsPerPage)
})

function selectAnswer(index, value) {
  answers.value[index] = value
  showValidation.value = false
}

function isCurrentPageAnswered() {
  return currentQuestions.value.every(question => answers.value[question.id - 1] !== null)
}

function isPageAnswered(pageIndex) {
  const start = pageIndex * questionsPerPage
  const pageQuestions = questions.slice(start, start + questionsPerPage)

  return pageQuestions.every(question => answers.value[question.id - 1] !== null)
}

function goNext() {
  if (!isCurrentPageAnswered()) {
    showValidation.value = true
    return
  }

  currentPage.value += 1
  showValidation.value = false
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goPrevious() {
  if (currentPage.value > 0) {
    currentPage.value -= 1
    showValidation.value = false
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function getScoredValue(question, answer) {
  return question.reverse ? 5 - answer : answer
}

function getResultBand(score) {
  if (score <= 34) return 'Well connected'
  if (score <= 49) return 'Some distance from others'
  if (score <= 64) return 'Moderate disconnection'
  return 'Feeling quite isolated'
}

function getResultExplanation(score) {
  if (score <= 34) return 'Your responses suggest a strong sense of social connection at the moment. You may still have occasional difficult feelings, but your wellbeing appears relatively stable.'
  if (score <= 49) return 'Your responses suggest some distance from others. This may mean that social connection, companionship, or emotional closeness feels reduced at times.'
  if (score <= 64) return 'Your responses suggest a moderate level of disconnection. You may be experiencing a noticeable gap in social or emotional connection in daily life.'
  return 'Your responses suggest a stronger feeling of disconnection. It could help to explore supportive social options or trusted people around you.'
}

function finishCheckIn() {
  if (!isCurrentPageAnswered()) {
    showValidation.value = true
    return
  }

  let score = 0
  const dimensions = { companionship: 0, socialConnection: 0, intimacy: 0 }

  questions.forEach((question, index) => {
    const answer = answers.value[index]
    const scored = answer !== null ? getScoredValue(question, answer) : 2

    score += scored
    dimensions[question.dimension] += scored
  })

  wellbeingStore.hasResult = true
  wellbeingStore.totalScore = score
  wellbeingStore.dimensionScores = { ...dimensions }
  wellbeingStore.resultBand = getResultBand(score)
  wellbeingStore.resultExplanation = getResultExplanation(score)

  router.push('/results')
}
</script>

<style scoped>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.checkin-page {
  min-height: 100vh; background: #f2faf0; color: #1a2e1e;
  font-family: system-ui, sans-serif; position: relative; overflow-x: hidden;
}

.noise {
  position: fixed; inset: 0; z-index: 1000; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
  background-size: 180px; opacity: 0.45;
}

.orb { position: fixed; border-radius: 50%; pointer-events: none; z-index: 0; filter: blur(80px); }
.orb-1 { width: 500px; height: 500px; background: rgba(90,180,110,0.18); top: -100px; left: -80px; animation: orb-drift 22s ease-in-out infinite alternate; }
.orb-2 { width: 380px; height: 380px; background: rgba(255,180,140,0.12); bottom: 5%; right: -60px; animation: orb-drift 28s ease-in-out infinite alternate-reverse; }
@keyframes orb-drift { 0%{transform:translate(0,0) scale(1)} 100%{transform:translate(40px,50px) scale(1.1)} }

.a-small { font-family: Georgia,serif; font-size: 13px; font-weight: 700; color: #0a9b8a; line-height: 1; }
.a-large { font-family: Georgia,serif; font-size: 22px; font-weight: 700; color: #0a9b8a; line-height: 1; }
.text-slider {
  -webkit-appearance: none; appearance: none;
  width: 120px; height: 4px;
  background: #d1e8d4; border-radius: 999px; outline: none; cursor: pointer;
}
.text-slider::-webkit-slider-thumb {
  -webkit-appearance: none; width: 22px; height: 22px; border-radius: 50%;
  background: #0a9b8a; box-shadow: 0 2px 8px rgba(10,155,138,0.4);
  cursor: pointer; transition: transform 0.2s;
}
.text-slider::-webkit-slider-thumb:hover { transform: scale(1.15); }
.text-slider:focus-visible { outline: 3px solid #0a9b8a; outline-offset: 3px; }
.scale-pct { font-size: 13px; font-weight: 700; color: #6a8e6e; min-width: 38px; }

.hero-band {
  position: relative; overflow: hidden;
  background: linear-gradient(160deg, #e4f5e0 0%, #c8edc8 100%);
  padding: 60px 52px 72px;
  border-bottom: 1px solid rgba(29,113,105,0.12);
  margin-top: 0;
}
.hero-bg-word {
  position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%);
  font-family: Georgia,serif; font-size: clamp(80px,14vw,180px);
  font-weight: 700; font-style: italic; color: rgba(10,155,138,0.055);
  white-space: nowrap; pointer-events: none; user-select: none; letter-spacing: -0.04em;
}
.hero-inner { position: relative; z-index: 2; max-width: 820px; }
.hero-eyebrow { display: inline-flex; align-items: center; gap: 12px; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #0a9b8a; margin-bottom: 20px; }
.eyebrow-line { display: block; width: 32px; height: 1px; background: #0a9b8a; }
.hero-headline { font-family: Georgia,serif; font-size: clamp(36px,5vw,72px); font-weight: 700; line-height: 1.08; color: #0f1e12; margin-bottom: 20px; }
.hero-headline em { color: #0a9b8a; font-style: italic; }
.hero-sub { font-size: 18px; line-height: 1.7; color: #4a6a4e; max-width: 680px; margin-bottom: 36px; }

.progress-wrap { display: flex; flex-direction: column; gap: 10px; max-width: 500px; }
.progress-track { width: 100%; height: 8px; background: rgba(29,113,105,0.15); border-radius: 999px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg,#0a9b8a,#5cb471); border-radius: 999px; transition: width 0.4s cubic-bezier(0.22,1,0.36,1); }
.progress-label { font-size: 14px; color: #6a8e6e; font-weight: 500; }
.progress-label strong { color: #0a9b8a; font-weight: 700; }

.main-wrap { position: relative; z-index: 2; max-width: 1200px; margin: 0 auto; padding: 52px 52px 100px; }
.questions-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 24px; margin-bottom: 32px; }

.question-card {
  background: white; border: 1px solid rgba(29,113,105,0.12);
  border-radius: 20px; padding: 48px;
  box-shadow: 0 16px 48px rgba(0,0,0,0.06);
  display: flex;
  flex-direction: column;
  height: 100%;
  animation: card-in 0.4s cubic-bezier(0.22,1,0.36,1);
}
@keyframes card-in { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: none; } }

.q-eyebrow { font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #0a9b8a; margin-bottom: 16px; }
.q-text { font-family: Georgia,serif; font-size: clamp(22px,3.5vw,36px); font-weight: 700; line-height: 1.3; color: #0f1e12; margin-bottom: 36px; }

.options { display: grid; grid-template-columns: repeat(2,1fr); gap: 14px; margin-top: auto; }

.option-btn {
  display: flex; align-items: center; gap: 14px;
  padding: 20px 24px; border: 1.5px solid rgba(29,113,105,0.2);
  border-radius: 14px; background: #f8fcf8;
  cursor: pointer; text-align: left;
  font-family: system-ui,sans-serif; font-weight: 600; color: #2a4a2e;
  transition: all 0.25s cubic-bezier(0.22,1,0.36,1);
}
.option-btn:hover { border-color: #0a9b8a; background: #f0faf0; transform: translateY(-2px); box-shadow: 0 8px 20px rgba(10,155,138,0.1); }
.option-btn.selected { border-color: #0a9b8a; background: linear-gradient(135deg,#e4f5e0,#d0eed0); color: #0a6b55; box-shadow: 0 8px 24px rgba(10,155,138,0.18); }
.option-btn:focus-visible { outline: 3px solid #0a9b8a; outline-offset: 2px; }

.option-indicator {
  width: 24px; height: 24px; border-radius: 50%;
  border: 2px solid rgba(10,155,138,0.3); background: white;
  flex-shrink: 0; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s; color: white;
}
.option-btn.selected .option-indicator { background: #0a9b8a; border-color: #0a9b8a; }
.option-label { font-weight: 600; }

.validation-msg {
  display: flex; align-items: center; gap: 8px;
  margin-top: 20px; padding: 12px 16px;
  background: #fff5f5; border: 1px solid rgba(200,50,50,0.2);
  border-radius: 10px; font-weight: 600; color: #b03030;
}

.nav-actions { display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }

.btn-primary, .btn-secondary {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 16px 28px; border-radius: 12px;
  font-weight: 700; cursor: pointer; border: none;
  font-family: system-ui,sans-serif;
  transition: all 0.25s cubic-bezier(0.22,1,0.36,1);
}
.btn-primary { background: linear-gradient(135deg,#0a9b8a,#056b5e); color: white; box-shadow: 0 10px 28px rgba(10,155,138,0.28); }
.btn-primary:hover { box-shadow: 0 16px 36px rgba(10,155,138,0.38); transform: translateY(-2px); }
.btn-finish { padding: 16px 36px; }
.btn-secondary { background: rgba(255,255,255,0.8); backdrop-filter: blur(8px); border: 1.5px solid rgba(29,113,105,0.2); color: #3a5a3e; }
.btn-secondary:hover { border-color: #0a9b8a; color: #0a9b8a; background: white; }
.btn-secondary:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }
.btn-primary:focus-visible, .btn-secondary:focus-visible { outline: 3px solid #0a9b8a; outline-offset: 3px; }

.dot-track { display: flex; align-items: center; gap: 5px; flex-wrap: wrap; justify-content: center; flex: 1; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: rgba(29,113,105,0.15); transition: all 0.3s cubic-bezier(0.22,1,0.36,1); }
.dot.answered { background: rgba(10,155,138,0.35); }
.dot.active { background: #0a9b8a; transform: scale(1.5); }

@media (max-width: 900px) {
  .hero-band { padding: 40px 20px 56px; margin-top: 0; }
  .main-wrap { padding: 32px 20px 80px; max-width: 820px; }
  .questions-grid { grid-template-columns: 1fr; gap: 16px; margin-bottom: 24px; }
  .question-card { padding: 28px 20px; }
  .options { grid-template-columns: 1fr; }
  .dot-track { display: none; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
</style>
