<template>
  <MainLayout>
    <section class="results-page">
      <div class="results-card">
        <template v-if="wellbeingStore.hasResult">
          <div class="results-header">
            <div>
              <p class="eyebrow">Wellbeing Check</p>
              <h2>Results</h2>
              <p class="intro">
                This result is based only on your current visit. It is not saved
                when you refresh or reopen the website.
              </p>
            </div>
          </div>

          <div class="score-box" :class="resultBandClass">
            <p class="score-label">Loneliness score</p>
            <div class="score-value">{{ wellbeingStore.totalScore }}</div>
            <p class="score-max">out of 80</p>
            <p class="score-band">{{ wellbeingStore.resultBand }}</p>
          </div>

          <div class="info-block">
            <h3>What this means</h3>
            <p>{{ wellbeingStore.resultExplanation }}</p>
            <p class="small-note">
              Some items are reverse scored to reflect positive social connection.
            </p>
          </div>

          <div class="dimension-grid">
            <div class="dimension-card">
              <p class="dimension-title">Companionship</p>
              <p class="dimension-score">
                {{ wellbeingStore.dimensionScores.companionship }}
              </p>
              <p class="dimension-desc">
                This reflects feelings of company, support, and not being alone.
              </p>
            </div>

            <div class="dimension-card">
              <p class="dimension-title">Social Connection</p>
              <p class="dimension-score">
                {{ wellbeingStore.dimensionScores.socialConnection }}
              </p>
              <p class="dimension-desc">
                This reflects belonging, shared interests, and connection with people around you.
              </p>
            </div>

            <div class="dimension-card">
              <p class="dimension-title">Intimacy</p>
              <p class="dimension-score">
                {{ wellbeingStore.dimensionScores.intimacy }}
              </p>
              <p class="dimension-desc">
                This reflects emotional closeness, trust, and having people you can turn to.
              </p>
            </div>
          </div>

          <div class="next-steps">
            <h3>Suggested next step</h3>
            <p>{{ nextStepText }}</p>
          </div>

          <div class="retake-block">
            <h3>Retake reminder</h3>
            <p>
              You may wish to retake this check-in in around 90 days to reflect
              on any changes over time.
            </p>
            <p class="small-note">
              This is shown as a privacy-safe suggestion only. The website does
              not save your answers or send reminders.
            </p>
          </div>

          <div class="page-actions">
            <RouterLink to="/checkin" class="secondary-btn">
              Back to Check-in
            </RouterLink>
          </div>
        </template>

        <template v-else>
          <div class="empty-state">
            <p class="eyebrow">Wellbeing Check</p>
            <h2>Results</h2>
            <p class="empty-text">
              No check-in result is available yet. Please complete the check-in first
              to see your score summary and explanation.
            </p>

            <div class="page-actions">
              <RouterLink to="/checkin" class="primary-btn">
                Go to Check-in
              </RouterLink>
            </div>
          </div>
        </template>
      </div>
    </section>
  </MainLayout>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import { wellbeingStore } from '../stores/wellbeingStore'

const resultBandClass = computed(() => {
  const score = wellbeingStore.totalScore

  if (score <= 34) return 'band-low'
  if (score <= 49) return 'band-mild'
  if (score <= 64) return 'band-moderate'
  return 'band-high'
})

const nextStepText = computed(() => {
  const score = wellbeingStore.totalScore

  if (score <= 34) {
    return 'Your score suggests a lower level of loneliness at the moment. You may still benefit from maintaining regular social contact and familiar routines.'
  }

  if (score <= 49) {
    return 'Your score suggests some distance from others. A small and manageable step, such as revisiting a familiar place or talking to someone you trust, may help.'
  }

  if (score <= 64) {
    return 'Your score suggests a moderate level of loneliness. Gentle social opportunities, familiar community spaces, or simple local activities may be helpful next steps.'
  }

  return 'Your score suggests a higher level of loneliness. It may help to start with low-pressure social options and reach out to trusted people or nearby support services when comfortable.'
})
</script>

<style scoped>
.results-page {
  margin: 28px;
}

.results-card {
  background: #fff;
  border: 1px solid #e5e6ef;
  border-radius: var(--radius-xl);
  padding: 32px;
  box-shadow: 0 10px 30px rgba(25, 32, 72, 0.06);
}

.results-header {
  margin-bottom: 24px;
}

.eyebrow {
  margin: 0 0 8px;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #6d7290;
}

.results-header h2,
.empty-state h2 {
  margin: 0 0 10px;
  font-family: 'Fraunces', serif;
  font-size: clamp(30px, 3vw, 42px);
  color: #2f3152;
}

.intro,
.empty-text {
  margin: 0;
  max-width: 760px;
  font-size: 17px;
  line-height: 1.6;
  color: #555973;
}

.score-box {
  border-radius: 24px;
  padding: 28px;
  margin-bottom: 28px;
  color: #2f3152;
}

.score-label {
  margin: 0 0 8px;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.score-value {
  font-size: 64px;
  font-weight: 800;
  line-height: 1;
}

.score-max {
  margin: 8px 0 14px;
  font-size: 20px;
  font-weight: 600;
}

.score-band {
  display: inline-block;
  margin: 0;
  padding: 10px 16px;
  border-radius: 999px;
  font-size: 15px;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.55);
}

.band-low {
  background: #eaf7ed;
}

.band-mild {
  background: #fff4dc;
}

.band-moderate {
  background: #ffe8d9;
}

.band-high {
  background: #fde2e2;
}

.info-block,
.next-steps,
.retake-block {
  margin-bottom: 28px;
}

.info-block h3,
.next-steps h3,
.retake-block h3 {
  margin: 0 0 10px;
  font-size: 22px;
  color: #2f3152;
}

.info-block p,
.next-steps p,
.retake-block p {
  margin: 0;
  font-size: 17px;
  line-height: 1.7;
  color: #555973;
}

.small-note {
  margin-top: 10px !important;
  font-size: 14px !important;
  color: #7a7f98 !important;
}

.dimension-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 28px;
}

.dimension-card {
  background: #f7f8fc;
  border: 1px solid #e6e8f2;
  border-radius: 20px;
  padding: 20px;
}

.dimension-title {
  margin: 0 0 10px;
  font-size: 15px;
  font-weight: 700;
  color: #6d7290;
}

.dimension-score {
  margin: 0 0 10px;
  font-size: 40px;
  font-weight: 800;
  color: #2f3152;
}

.dimension-desc {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #666b86;
}

.page-actions {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.primary-btn,
.secondary-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  border: none;
  border-radius: 14px;
  padding: 14px 22px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s ease;
}

.primary-btn {
  background: #ff7d57;
  color: #fff;
}

.primary-btn:hover {
  background: #ef6e47;
}

.secondary-btn {
  background: #eef0f7;
  color: #3f4568;
}

.secondary-btn:hover {
  background: #e2e6f2;
}

.empty-state {
  min-height: 320px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

@media (max-width: 900px) {
  .results-card {
    padding: 22px;
  }

  .dimension-grid {
    grid-template-columns: 1fr;
  }

  .score-value {
    font-size: 52px;
  }
}
</style>