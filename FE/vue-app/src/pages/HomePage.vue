<template>
  <div class="home-page">
    <header class="top-nav">
      <div class="brand">
        <div class="logo-circle">●</div>
        <div>
          <h1><span>Connect</span>Local</h1>
          <p>Real connections. Local places.</p>
        </div>
      </div>

      <nav class="nav-links">
        <RouterLink to="/home">Home</RouterLink>
        <RouterLink to="/checkin">Events</RouterLink>
        <RouterLink to="/discover">Places</RouterLink>
        <RouterLink to="/about">About</RouterLink>
        <RouterLink to="/resources">Resources</RouterLink>
        <RouterLink to="/checkin" class="start-btn">Start Check-in</RouterLink>
      </nav>
    </header>

    <section class="hero">
      <div class="hero-text">
        <h2>
          You're not<br />
          alone in this.
        </h2>

        <p>
          People of all ages experience challenges with social connection and
          wellbeing.
        </p>
        <p>
          Small steps can help build a more connected life.
        </p>

        <RouterLink to="/checkin" class="explore-btn">
          Explore activities near you
        </RouterLink>
      </div>

      <div class="hero-art">
        <div class="tree tree-left"></div>
        <div class="tree tree-middle"></div>
        <div class="tree tree-right"></div>

        <div class="sun"></div>

        <div class="bench"></div>
        <div class="person person-left"></div>
        <div class="person person-right"></div>
      </div>
    </section>

    <section class="age-section">
      <div class="age-text">
        <h2>Understanding wellbeing across age groups</h2>
        <p>
          Around the country, people of every age experience periods of higher
          psychological distress. Select your age group to see how common this is
          and know you are not alone.
        </p>
      </div>

      <div class="age-panel">
        <label for="ageGroup">Select your age group</label>

        <select id="ageGroup" v-model="selectedAgeGroup">
          <option value="">Choose your age group...</option>
          <option
            v-for="item in distressData"
            :key="item.age_group"
            :value="item.age_group"
          >
            {{ formatAgeGroup(item.age_group) }}
          </option>
        </select>

        <p v-if="isLoading" class="loading-text">
          Loading wellbeing data...
        </p>

        <p v-if="loadError" class="error-text">
          {{ loadError }}
        </p>

        <div v-if="selectedRecord" class="age-result">
          <h3>
            Around {{ selectedRecord.psychological_distress_percent }}% of people aged
            {{ formatAgeGroup(selectedRecord.age_group) }} experience higher levels
            of psychological distress.
          </h3>

          <p>
            This helps show that wellbeing challenges can affect people across
            different age groups. You are not alone, and ConnectLocal can help
            you find welcoming local activities.
          </p>

          <p v-if="elderlyNote" class="elderly-note">
            {{ elderlyNote }}
          </p>

          <p class="source">
            Source: {{ sourceText }}
          </p>
        </div>
      </div>
    </section>

    <section class="steps-section">
      <h2>Small steps can help</h2>
      <p>
        Being part of your local community and finding places to connect can
        improve wellbeing and reduce feelings of isolation.
      </p>

      <div class="step-grid">
        <div class="step-card">
          <div class="step-icon mint">⌖</div>
          <h3>Local places</h3>
          <p>Find nearby places that feel familiar and easy to reach.</p>
        </div>

        <div class="step-card">
          <div class="step-icon yellow">◒</div>
          <h3>Gentle activities</h3>
          <p>Explore simple activities that do not feel too stressful.</p>
        </div>

        <div class="step-card">
          <div class="step-icon pink">♿</div>
          <h3>Comfort focused</h3>
          <p>Consider access, comfort and ease before going out.</p>
        </div>

        <div class="step-card">
          <div class="step-icon purple">♡</div>
          <h3>Social connection</h3>
          <p>Take small steps to reconnect with people around you.</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

const API_URL = 'https://connectlocal.duckdns.org/api/suburbs/psychological-distress'

const selectedAgeGroup = ref('')
const distressData = ref([])
const sourceText = ref('ABS National Health Survey')
const elderlyHighlight = ref(null)
const isLoading = ref(false)
const loadError = ref('')

const selectedRecord = computed(() => {
  return distressData.value.find(
    item => item.age_group === selectedAgeGroup.value
  )
})

const elderlyNote = computed(() => {
  if (!elderlyHighlight.value || !selectedRecord.value) return ''

  if (selectedRecord.value.age_group === elderlyHighlight.value.age_group) {
    return elderlyHighlight.value.note
  }

  return ''
})

function formatAgeGroup(ageGroup) {
  if (ageGroup === '65+') return '65 years and over'
  return `${ageGroup} years`
}

async function fetchDistressData() {
  isLoading.value = true
  loadError.value = ''

  try {
    const response = await fetch(API_URL)

    if (!response.ok) {
      throw new Error('Failed to load data')
    }

    const result = await response.json()

    distressData.value = result.data || []
    elderlyHighlight.value = result.elderly_highlight || null

    if (result.source && result.year) {
      sourceText.value = `${result.source}, ${result.year}`
    }
  } catch (error) {
    loadError.value = 'Unable to load wellbeing data right now.'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchDistressData()
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #f7faf7;
  color: #2f2d42;
}

.top-nav {
  height: 92px;
  padding: 0 44px;
  background: #fff;
  border-bottom: 2px solid #d9d8e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
}

.logo-circle {
  width: 52px;
  height: 52px;
  background: #078d7f;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.brand h1 {
  margin: 0;
  font-family: Georgia, serif;
  font-size: calc(28px * var(--font-scale));
  line-height: 1;
}

.brand h1 span {
  color: #1f2c1f;
}

.brand h1 {
  color: #078d7f;
}

.brand p {
  margin: 4px 0 0;
  font-size: calc(16px * var(--font-scale));
  font-weight: 700;
  color: #5f6075;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 28px;
}

.nav-links a {
  text-decoration: none;
  color: #4b4b61;
  font-size: calc(18px * var(--font-scale));
  font-weight: 800;
}

.nav-links .router-link-active {
  color: #1d7169;
  border-bottom: 3px solid #1d7169;
  padding-bottom: 8px;
}

.start-btn {
  border: 3px solid #1d7169;
  border-radius: 999px;
  padding: 12px 24px;
  color: #1d7169 !important;
  border-bottom: 3px solid #1d7169 !important;
}

.hero {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 560px;
  border-bottom: 2px solid #d9d8e6;
}

.hero-text {
  padding: 88px 68px;
  background: #f7fbf8;
}

.hero-text h2 {
  margin: 0 0 28px;
  font-family: Georgia, serif;
  font-size: calc(64px * var(--font-scale));
  line-height: 1.08;
  color: #17341d;
}

.hero-text p {
  margin: 0 0 14px;
  font-size: calc(24px * var(--font-scale));
  line-height: 1.5;
  color: #48564b;
}

.explore-btn {
  display: inline-block;
  margin-top: 28px;
  background: #008c7d;
  color: #fff;
  text-decoration: none;
  padding: 20px 34px;
  border-radius: 14px;
  font-size: calc(22px * var(--font-scale));
  font-weight: 800;
  box-shadow: 0 14px 28px rgba(0, 140, 125, 0.25);
}

.hero-art {
  position: relative;
  overflow: hidden;
  background: #d8efd2;
}

.tree {
  position: absolute;
  border-radius: 50%;
  background: rgba(82, 160, 90, 0.35);
}

.tree-left {
  width: 170px;
  height: 220px;
  left: 40px;
  top: 150px;
}

.tree-middle {
  width: 250px;
  height: 180px;
  left: 250px;
  top: 100px;
}

.tree-right {
  width: 200px;
  height: 240px;
  right: 40px;
  top: 100px;
}

.sun {
  position: absolute;
  width: 96px;
  height: 96px;
  right: 120px;
  top: 70px;
  background: rgba(255, 255, 220, 0.55);
  border-radius: 50%;
}

.bench {
  position: absolute;
  width: 330px;
  height: 22px;
  left: 260px;
  bottom: 170px;
  background: #9a7445;
  border-radius: 6px;
}

.person {
  position: absolute;
  width: 90px;
  height: 140px;
  bottom: 170px;
  border-radius: 28px 28px 12px 12px;
}

.person-left {
  left: 285px;
  background: #35537a;
}

.person-right {
  left: 465px;
  background: #cabb9a;
}

.age-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 70px;
  padding: 70px 56px;
  background: #fff;
  border-bottom: 2px solid #e1e2ea;
}

.age-text h2 {
  margin: 0 0 26px;
  font-family: Georgia, serif;
  font-size: calc(40px * var(--font-scale));
  line-height: 1.2;
}

.age-text p {
  margin: 0;
  font-size: calc(22px * var(--font-scale));
  line-height: 1.6;
  color: #5d5d75;
}

.age-panel label {
  display: block;
  margin-bottom: 10px;
  font-size: calc(20px * var(--font-scale));
  font-weight: 800;
  color: #5d5d75;
}

.age-panel select {
  width: 100%;
  padding: 18px 22px;
  border: 3px solid #1b8179;
  border-radius: 14px;
  background: #fff;
  font-size: calc(22px * var(--font-scale));
  font-weight: 800;
  color: #2f2d42;
}

.loading-text,
.error-text {
  margin-top: 14px;
  font-size: calc(16px * var(--font-scale));
  font-weight: 700;
}

.error-text {
  color: #b3261e;
}

.age-result {
  margin-top: 20px;
  padding: 26px 30px;
  border-left: 6px solid #1b8179;
  border-radius: 0 16px 16px 0;
  background: #eff8f6;
}

.age-result h3 {
  margin: 0 0 12px;
  font-size: calc(22px * var(--font-scale));
}

.age-result p {
  margin: 0 0 10px;
  font-size: calc(18px * var(--font-scale));
  line-height: 1.6;
  color: #5d5d75;
}

.elderly-note {
  font-weight: 700;
  color: #1b8179;
}

.source {
  font-size: calc(15px * var(--font-scale)) !important;
}

.steps-section {
  padding: 72px 56px;
  background: #f7faf7;
  text-align: center;
}

.steps-section h2 {
  margin: 0 0 16px;
  font-family: Georgia, serif;
  font-size: calc(38px * var(--font-scale));
}

.steps-section > p {
  max-width: 780px;
  margin: 0 auto 44px;
  font-size: calc(22px * var(--font-scale));
  line-height: 1.6;
  color: #5d5d75;
}

.step-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 28px;
}

.step-card {
  background: #fff;
  border: 2px solid #dfe8df;
  border-radius: 18px;
  padding: 34px 24px;
}

.step-icon {
  width: 70px;
  height: 70px;
  margin: 0 auto 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: calc(32px * var(--font-scale));
}

.mint {
  background: #e3faf5;
}

.yellow {
  background: #fff8d8;
}

.pink {
  background: #fff0ed;
}

.purple {
  background: #eee5ff;
}

.step-card h3 {
  margin: 0 0 12px;
  font-size: calc(22px * var(--font-scale));
}

.step-card p {
  margin: 0;
  font-size: calc(18px * var(--font-scale));
  line-height: 1.5;
  color: #5d5d75;
}

@media (max-width: 1000px) {
  .top-nav {
    height: auto;
    padding: 22px;
    flex-direction: column;
    gap: 18px;
  }

  .nav-links {
    flex-wrap: wrap;
    justify-content: center;
  }

  .hero,
  .age-section {
    grid-template-columns: 1fr;
  }

  .hero-text h2 {
    font-size: calc(46px * var(--font-scale));
  }

  .step-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>