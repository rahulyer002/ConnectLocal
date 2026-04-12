<template>
  <MainLayout>
    <section class="hero">
      <h2>Find your next <em>warm moment</em></h2>
      <p>Free and low-cost activities near Sunshine</p>

      <button class="location-picker">
        <span>Sunshine, VIC 3020</span>
        <span>Change</span>
      </button>

      <div class="chips">
        <button class="chip solid">Free</button>
        <button class="chip solid">This Week</button>
        <button class="chip solid">Recommended for You</button>
        <button class="chip">Nearby</button>
        <button class="chip">Arts</button>
        <button class="chip">Wellness</button>
      </div>
    </section>

    <section class="results-header">
      <h3>3 activities this week</h3>
      <button class="print-btn">Print list</button>
    </section>

    <section class="activity-list">
      <article class="event-card">
        <div class="tags">
          <span class="tag green">Free</span>
          <span class="tag lilac">Most Popular</span>
          <span class="distance">1.2 km</span>
        </div>
        <h4>Watercolour Morning for Seniors</h4>
        <p class="meta">Tue 1 Apr · 9:30 AM · Fitzroy Library</p>
        <p class="desc">
          A relaxed morning painting session with all materials provided. No
          experience needed, just turn up and enjoy.
        </p>
        <div class="event-foot">
          <span>8 spots left</span>
          <a href="#">View details →</a>
        </div>
      </article>

      <article class="event-card">
        <div class="tags">
          <span class="tag green">Free</span>
          <span class="tag lilac">Near You</span>
          <span class="distance">0.4 km</span>
        </div>
        <h4>Sunshine Community Cafe Meetup</h4>
        <p class="meta">Wed 2 Apr · 10:00 AM · Hampshire Rd</p>
        <p class="desc">
          Meet locals over coffee and board games in a friendly group setting.
          New faces are always welcome.
        </p>
        <div class="event-foot">
          <span>12 spots left</span>
          <a href="#">View details →</a>
        </div>
      </article>
    </section>
  </MainLayout>
</template>

<script setup>
import MainLayout from '../layouts/MainLayout.vue'
</script>

<style scoped>
.hero {
  background: linear-gradient(135deg, var(--orange) 0%, var(--orange-deep) 100%);
  color: #fff;
  padding: 30px 28px;
}

.hero h2 {
  margin: 0;
  font-family: 'Fraunces', serif;
  font-size: clamp(36px, 4vw, 56px);
  line-height: 1;
}

.hero h2 em {
  color: #ffd24d;
  font-style: italic;
}

.hero p {
  margin: 10px 0 20px;
  font-size: clamp(18px, 2.2vw, 34px);
  font-weight: 600;
}

.location-picker {
  width: 100%;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
  padding: 14px 18px;
  font-size: clamp(18px, 2vw, 28px);
  font-weight: 800;
  display: flex;
  justify-content: space-between;
}

.chips {
  margin-top: 18px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.chip {
  border-radius: 999px;
  border: 2px solid rgba(255, 255, 255, 0.65);
  background: transparent;
  color: #fff;
  padding: 10px 16px;
  font-size: 20px;
  font-weight: 800;
}

.chip.solid {
  border-color: #b08b0a;
  background: var(--yellow);
  color: #1f1d1a;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 22px 24px 12px;
}

.results-header h3 {
  margin: 0;
  font-size: clamp(24px, 2.5vw, 36px);
}

.print-btn {
  border: 2px solid #c7c8dc;
  border-radius: 999px;
  background: transparent;
  color: #616580;
  font-size: 16px;
  padding: 8px 14px;
  font-weight: 700;
}

.activity-list {
  padding: 0 18px 24px;
  display: grid;
  gap: 14px;
}

.event-card {
  background: var(--panel-2);
  border: 2px solid #cbccdf;
  border-radius: var(--radius-xl);
  padding: 20px;
}

.tags {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tag {
  border-radius: 999px;
  padding: 7px 13px;
  font-size: 16px;
  font-weight: 800;
}

.tag.green {
  background: #088f7e;
  color: #fff;
}

.tag.lilac {
  background: #d9d0f5;
  color: #4a42a8;
}

.distance {
  margin-left: auto;
  background: #caece7;
  border: 2px solid #a2d8d1;
  color: #0c7f72;
  border-radius: 14px;
  padding: 7px 11px;
  font-size: 16px;
  font-weight: 800;
}

.event-card h4 {
  margin: 16px 0 8px;
  font-family: 'Fraunces', serif;
  font-size: clamp(30px, 3vw, 46px);
  line-height: 1.08;
}

.meta {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #565973;
}

.desc {
  margin: 14px 0 18px;
  font-size: 20px;
  line-height: 1.35;
  color: #41445b;
}

.event-foot {
  border-top: 2px solid #d7d7e5;
  padding-top: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 20px;
  font-weight: 800;
}

.event-foot a {
  color: #06786f;
}

@media (max-width: 980px) {
  .results-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .event-foot {
    font-size: 17px;
  }
}
</style>
