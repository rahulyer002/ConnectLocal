<template>
  <MainLayout>
    <section class="checkin-page">
      <div class="checkin-card">
        <div class="checkin-header">
          <div>
            <p class="eyebrow">Wellbeing Check</p>
            <h2>Check-in Questions</h2>
            <p class="intro">
              Answer the questions based on how often you feel this way.
              Your answers are only used for this visit and are not saved.
            </p>
          </div>

          <div class="progress-block">
            <span class="progress-text">
              Question {{ currentQuestionNumber }} of {{ questions.length }}
            </span>
            <div class="progress-bar">
              <div
                class="progress-fill"
                :style="{ width: progressPercent + '%' }"
              ></div>
            </div>
          </div>
        </div>

        <div class="question-card">
          <p class="question-number">Statement {{ currentQuestion.id }}</p>
          <h3 class="question-text">{{ currentQuestion.text }}</h3>

          <div class="options">
            <button
              v-for="option in options"
              :key="option.value"
              class="option-btn"
              :class="{ selected: answers[currentQuestionIndex] === option.value }"
              @click="selectAnswer(option.value)"
            >
              <span class="option-label">{{ option.label }}</span>
            </button>
          </div>

          <p v-if="showValidation" class="validation-text">
            Please choose one answer before continuing.
          </p>
        </div>

        <div class="nav-actions">
          <button
            class="secondary-btn"
            @click="goPrevious"
            :disabled="currentQuestionIndex === 0"
          >
            Previous
          </button>

          <button
            v-if="!isLastQuestion"
            class="primary-btn"
            @click="goNext"
          >
            Next
          </button>

          <button
            v-else
            class="primary-btn"
            @click="finishCheckIn"
          >
            Finish
          </button>
        </div>
      </div>
    </section>
  </MainLayout>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import { wellbeingStore } from '../stores/wellbeingStore'

const router = useRouter()

const options = [
  { label: 'Never', value: 1 },
  { label: 'Rarely', value: 2 },
  { label: 'Sometimes', value: 3 },
  { label: 'Often', value: 4 }
]

const questions = [
  {
    id: 1,
    text: 'How often do you feel that you are "in tune" with the people around you?',
    reverse: true,
    dimension: 'socialConnection'
  },
  {
    id: 2,
    text: 'How often do you feel that you lack companionship?',
    reverse: false,
    dimension: 'companionship'
  },
  {
    id: 3,
    text: 'How often do you feel that there is no one you can turn to?',
    reverse: false,
    dimension: 'intimacy'
  },
  {
    id: 4,
    text: 'How often do you feel alone?',
    reverse: false,
    dimension: 'companionship'
  },
  {
    id: 5,
    text: 'How often do you feel part of a group of friends?',
    reverse: true,
    dimension: 'socialConnection'
  },
  {
    id: 6,
    text: 'How often do you feel that you have a lot in common with the people around you?',
    reverse: true,
    dimension: 'socialConnection'
  },
  {
    id: 7,
    text: 'How often do you feel that you are no longer close to anyone?',
    reverse: false,
    dimension: 'intimacy'
  },
  {
    id: 8,
    text: 'How often do you feel that your interests and ideas are not shared by those around you?',
    reverse: false,
    dimension: 'socialConnection'
  },
  {
    id: 9,
    text: 'How often do you feel outgoing and friendly?',
    reverse: true,
    dimension: 'socialConnection'
  },
  {
    id: 10,
    text: 'How often do you feel close to people?',
    reverse: true,
    dimension: 'intimacy'
  },
  {
    id: 11,
    text: 'How often do you feel left out?',
    reverse: false,
    dimension: 'socialConnection'
  },
  {
    id: 12,
    text: 'How often do you feel that your relationships with others are not meaningful?',
    reverse: false,
    dimension: 'intimacy'
  },
  {
    id: 13,
    text: 'How often do you feel that no one really knows you well?',
    reverse: false,
    dimension: 'intimacy'
  },
  {
    id: 14,
    text: 'How often do you feel isolated from others?',
    reverse: false,
    dimension: 'companionship'
  },
  {
    id: 15,
    text: 'How often do you feel you can find companionship when you want it?',
    reverse: true,
    dimension: 'companionship'
  },
  {
    id: 16,
    text: 'How often do you feel that there are people who really understand you?',
    reverse: true,
    dimension: 'intimacy'
  },
  {
    id: 17,
    text: 'How often do you feel shy?',
    reverse: false,
    dimension: 'socialConnection'
  },
  {
    id: 18,
    text: 'How often do you feel that people are around you but not with you?',
    reverse: false,
    dimension: 'companionship'
  },
  {
    id: 19,
    text: 'How often do you feel that there are people you can talk to?',
    reverse: true,
    dimension: 'intimacy'
  },
  {
    id: 20,
    text: 'How often do you feel that there are people you can turn to?',
    reverse: true,
    dimension: 'intimacy'
  }
]

const currentQuestionIndex = ref(0)
const answers = ref(Array(questions.length).fill(null))
const showValidation = ref(false)

const currentQuestion = computed(() => questions[currentQuestionIndex.value])
const currentQuestionNumber = computed(() => currentQuestionIndex.value + 1)
const isLastQuestion = computed(() => currentQuestionIndex.value === questions.length - 1)
const progressPercent = computed(() => ((currentQuestionIndex.value + 1) / questions.length) * 100)

function selectAnswer(value) {
  answers.value[currentQuestionIndex.value] = value
  showValidation.value = false
}

function goNext() {
  if (answers.value[currentQuestionIndex.value] === null) {
    showValidation.value = true
    return
  }

  currentQuestionIndex.value += 1
  showValidation.value = false
}

function goPrevious() {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value -= 1
    showValidation.value = false
  }
}

function getScoredValue(question, answer) {
  return question.reverse ? 5 - answer : answer
}

function getResultBand(score) {
  if (score <= 34) return 'Low loneliness'
  if (score <= 49) return 'Some distance from others'
  if (score <= 64) return 'Moderate loneliness'
  return 'High loneliness'
}

function getResultExplanation(score) {
  if (score <= 34) {
    return 'Your responses suggest a lower level of loneliness at the moment. You may still have occasional difficult feelings, but your social connection appears relatively stable.'
  }

  if (score <= 49) {
    return 'Your responses suggest some distance from others. This may mean that social connection, companionship, or emotional closeness feels reduced at times.'
  }

  if (score <= 64) {
    return 'Your responses suggest a moderate level of loneliness. You may be experiencing a noticeable gap in social or emotional connection in daily life.'
  }

  return 'Your responses suggest a high level of loneliness. This may indicate a stronger feeling of disconnection, and it could help to explore supportive social options or trusted people around you.'
}

function finishCheckIn() {
  if (answers.value[currentQuestionIndex.value] === null) {
    showValidation.value = true
    return
  }

  let score = 0
  const dimensions = {
    companionship: 0,
    socialConnection: 0,
    intimacy: 0
  }

  questions.forEach((question, index) => {
    const scoredValue = getScoredValue(question, answers.value[index])
    score += scoredValue
    dimensions[question.dimension] += scoredValue
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
.checkin-page {
  margin: 28px;
}

.checkin-card {
  background: #fff;
  border: 1px solid #e5e6ef;
  border-radius: var(--radius-xl);
  padding: 32px;
  box-shadow: 0 10px 30px rgba(25, 32, 72, 0.06);
}

.checkin-header {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 28px;
  flex-wrap: wrap;
}

.eyebrow {
  margin: 0 0 8px;
  font-size: calc(14px * var(--font-scale));
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #6d7290;
}

.checkin-header h2 {
  margin: 0 0 10px;
  font-family: 'Fraunces', serif;
  font-size: calc(36px * var(--font-scale));
  color: #2f3152;
}

.intro {
  margin: 0;
  max-width: 760px;
  font-size: calc(17px * var(--font-scale));
  line-height: 1.6;
  color: #555973;
}

.progress-block {
  min-width: 280px;
  flex: 1;
  max-width: 360px;
}

.progress-text {
  display: inline-block;
  margin-bottom: 10px;
  font-size: calc(14px * var(--font-scale));
  font-weight: 600;
  color: #6d7290;
}

.progress-bar {
  width: 100%;
  height: 12px;
  background: #ececf3;
  border-radius: 999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #0c8b7d, #4bb6a8);
  border-radius: 999px;
  transition: width 0.25s ease;
}

.question-card {
  border: 1px solid #e8e9f3;
  border-radius: 24px;
  padding: 28px;
  background: #fcfcff;
}

.question-number {
  margin: 0 0 10px;
  font-size: calc(14px * var(--font-scale));
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #6d7290;
}

.question-text {
  margin: 0 0 24px;
  font-size: calc(30px * var(--font-scale));
  line-height: 1.3;
  font-family: 'Fraunces', serif;
  color: #2f3152;
}

.options {
  display: grid;
  grid-template-columns: repeat(2, minmax(180px, 1fr));
  gap: 16px;
}

.option-btn {
  border: 2px solid #e2e3ef;
  border-radius: 18px;
  background: #fff;
  padding: 18px 20px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: calc(18px * var(--font-scale));
  font-weight: 600;
  color: #444866;
}

.option-btn:hover {
  border-color: #0c8b7d;
  transform: translateY(-1px);
}

.option-btn.selected {
  border-color: #0c8b7d;
  background: #e3faf5;
  color: #0c8b7d;
}

.option-label {
  display: block;
}

.validation-text {
  margin: 16px 0 0;
  font-size: calc(15px * var(--font-scale));
  font-weight: 600;
  color: #c84848;
}

.nav-actions {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-top: 24px;
  flex-wrap: wrap;
}

.primary-btn,
.secondary-btn {
  border: none;
  border-radius: 14px;
  padding: 14px 22px;
  font-size: calc(16px * var(--font-scale));
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s ease;
}

.primary-btn {
  background: #0c8b7d;
  color: #fff;
}

.primary-btn:hover {
  background: #0a756a;
}

.secondary-btn {
  background: #eef0f7;
  color: #3f4568;
}

.secondary-btn:hover {
  background: #e2e6f2;
}

.secondary-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 900px) {
  .options {
    grid-template-columns: 1fr;
  }

  .checkin-card {
    padding: 22px;
  }

  .question-card {
    padding: 22px;
  }
}
</style>