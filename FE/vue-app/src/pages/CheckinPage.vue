<template>
  <MainLayout>
    <section class="checkin-landing">
      <div class="hero-section">
        <div class="hero-badge">
          <span>☆</span>
          <span>Your weekly wellbeing check-in</span>
        </div>

        <h1>
          How are you feeling<br />
          <em>about your connections?</em>
        </h1>

        <p>
          This gentle 5-minute check-in helps you understand how connected you
          feel to the people around you, and points you toward warm, welcoming
          activities in your neighbourhood.
        </p>

        <div class="circle circle-large"></div>
        <div class="circle circle-small"></div>
      </div>

      <div class="content-section">
        <div class="info-card">
          <div class="icon-box pink">☺</div>
          <div>
            <h3>20 simple questions</h3>
            <p>
              Easy to answer, no right or wrong. Just how you honestly feel
              right now.
            </p>
          </div>
        </div>

        <div class="info-card">
          <div class="icon-box mint">▥</div>
          <div>
            <h3>A clear picture of your wellbeing</h3>
            <p>
              See which areas of connection are going well and which need a
              little attention.
            </p>
          </div>
        </div>

        <div class="info-card">
          <div class="icon-box yellow">▣</div>
          <div>
            <h3>Activities matched to you</h3>
            <p>
              Discover free, nearby events chosen to suit your situation and
              interests.
            </p>
          </div>
        </div>

        <button class="start-button" @click="startCheckin">
          Start My Check-in
          <span>›</span>
        </button>

        <p class="note">Anonymous · Nothing is stored · Takes about 5 minutes</p>
      </div>
    </section>
  </MainLayout>
</template>

<script setup>
import { useRouter } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'

const router = useRouter()

function startCheckin() {
  router.push('/checkin/form')
}
</script>

<style scoped>
.checkin-landing {
  width: 100%;
  min-height: 100vh;
  background: #fbfaf8;
}

.hero-section {
  position: relative;
  overflow: hidden;
  padding: 80px 64px 72px;
  background: linear-gradient(135deg, #0c8b7d, #0a756a);
  color: white;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 10px 24px;
  margin-bottom: 28px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.22);
  font-size: calc(18px * var(--font-scale));
  font-weight: 700;
}

.hero-section h1 {
  position: relative;
  z-index: 2;
  margin: 0 0 24px;
  font-family: Georgia, serif;
  font-size: calc(56px * var(--font-scale));
  line-height: 1.15;
  font-weight: 500;
}

.hero-section em {
  color: #ffc83d;
  font-style: italic;
}

.hero-section p {
  position: relative;
  z-index: 2;
  max-width: 1100px;
  margin: 0;
  font-size: calc(24px * var(--font-scale));
  line-height: 1.7;
  font-weight: 500;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.14);
}

.circle-large {
  width: 230px;
  height: 230px;
  right: -45px;
  top: -45px;
}

.circle-small {
  width: 180px;
  height: 180px;
  left: -55px;
  bottom: -70px;
}

.content-section {
  padding: 38px 42px 36px;
}

.info-card {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 28px 32px;
  margin-bottom: 24px;
  background: white;
  border: 3px solid #d9d5e8;
  border-radius: 26px;
}

.icon-box {
  width: 64px;
  height: 64px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 20px;
  font-size: calc(30px * var(--font-scale));
  font-weight: 700;
  color: #2f2d42;
}

.pink {
  background: #e3faf5;
}

.mint {
  background: #e4faf5;
}

.yellow {
  background: #fff8d8;
}

.info-card h3 {
  margin: 0 0 10px;
  font-size: calc(28px * var(--font-scale));
  color: #29263a;
}

.info-card p {
  margin: 0;
  font-size: calc(24px * var(--font-scale));
  line-height: 1.5;
  color: #6d6984;
}

.start-button {
  width: 100%;
  margin-top: 14px;
  padding: 26px 32px;
  border: none;
  border-radius: 22px;
  background: #0c8b7d;
  color: white;
  font-size: calc(30px * var(--font-scale));
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 14px 28px rgba(12, 139, 125, 0.28);
}

.start-button:hover {
  transform: translateY(-2px);
  background: #0a756a;
}

.start-button span {
  margin-left: 10px;
  font-size: calc(36px * var(--font-scale));
}

.note {
  margin: 22px 0 0;
  text-align: center;
  font-size: calc(18px * var(--font-scale));
  color: #6d6984;
}

@media (max-width: 900px) {
  .hero-section {
    padding: 56px 28px;
  }

  .hero-section h1 {
    font-size: calc(40px * var(--font-scale));
  }

  .hero-section p {
    font-size: calc(18px * var(--font-scale));
  }

  .content-section {
    padding: 28px 20px;
  }

  .info-card {
    align-items: flex-start;
    padding: 24px;
  }

  .info-card h3 {
    font-size: calc(22px * var(--font-scale));
  }

  .info-card p {
    font-size: calc(18px * var(--font-scale));
  }

  .start-button {
    font-size: calc(24px * var(--font-scale));
  }
}
</style>