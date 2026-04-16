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
