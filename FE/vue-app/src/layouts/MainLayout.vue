
<template>
  <div class="app-frame">
    <aside class="sidebar">
      <div class="brand-card">
        <h1><span>Connect</span>Local</h1>
        <p>Emily · Sunshine, VIC</p>
      </div>

      <nav class="side-nav">
        <RouterLink to="/checkin" class="nav-item">Wellbeing Check</RouterLink>
        <RouterLink to="/discover" class="nav-item">Discover Events</RouterLink>
      </nav>

      <section class="score-card">
        <p class="score-label">WELLBEING SCORE</p>
        <p class="score-value">48</p>
        <p class="score-sub">out of 80</p>
        <span class="score-tag">Some distance from others</span>
      </section>
    </aside>

    <main class="main">
      <nav class="top-tabs" v-if="route.path !== '/discover'">
        <RouterLink to="/checkin">Check-in</RouterLink>
        <RouterLink to="/results">Results</RouterLink>
        <RouterLink to="/discover">Discover</RouterLink>
      </nav>

      <section class="page-content">
        <slot />
      </section>
    </main>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<style scoped>
.app-frame {
  min-height: 100vh;
  overflow: hidden;
  display: grid;
  grid-template-columns: var(--sidebar-width) minmax(0, 1fr);
  background: var(--panel);
}

.sidebar {
  background: #d8d9e3;
  border-right: 1px solid #cbccdb;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.brand-card {
  padding: 34px 26px 24px;
  border-bottom: 1px solid var(--line);
}

.brand-card h1 {
  margin: 0;
  font-family: 'Fraunces', serif;
  font-size: clamp(30px, 3vw, 46px);
  line-height: 1;
}

.brand-card h1 span {
  color: #f56a48;
}

.brand-card p {
  margin: 10px 0 0;
  color: var(--muted);
  font-weight: 700;
}

.side-nav {
  padding: 14px 0;
}

.nav-item {
  display: block;
  padding: 18px 26px;
  font-size: 20px;
  font-weight: 700;
  color: #5f617f;
  border-left: 5px solid transparent;
  transition: all 0.2s ease;
  cursor: pointer;
  user-select: none;
}

.nav-item:hover {
  background: #f0e8eb;
  border-left-color: #f5a89f;
  color: #4a4c65;
}

.nav-item.router-link-exact-active {
  background: #efdfe3;
  border-left-color: #f06e50;
  color: #33354d;
}

.score-card {
  margin: auto 20px 24px;
  background: #f2f2f7;
  border: 1px solid #d8d8e8;
  border-radius: var(--radius-lg);
  padding: 22px;
}

.score-label {
  margin: 0;
  color: #696b8a;
  font-size: 13px;
  letter-spacing: 0.08em;
  font-weight: 800;
}

.score-value {
  margin: 14px 0 2px;
  font-family: 'Fraunces', serif;
  font-size: 54px;
  color: #e0a700;
}

.score-sub {
  margin: 0;
  color: #666988;
  font-weight: 700;
}

.score-tag {
  display: inline-block;
  margin-top: 14px;
  background: #f1e8c9;
  color: #86660d;
  border-radius: 12px;
  padding: 8px 12px;
  font-size: 14px;
  font-weight: 800;
}

.main {
  background: #f5f5fa;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.top-tabs {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border-bottom: 1px solid var(--line);
  background: #fff;
}

.top-tabs a {
  text-align: center;
  padding: 20px 14px;
  font-size: 24px;
  color: #626682;
  font-weight: 700;
  border-bottom: 4px solid transparent;
}

.top-tabs a.router-link-exact-active {
  color: #f26648;
  border-bottom-color: #f26648;
}

.page-content {
  flex: 1;
}

@media (max-width: 1280px) {
  .brand-card {
    padding: 26px 20px 18px;
  }

  .side-nav {
    padding: 10px 0;
  }

  .nav-item {
    padding: 14px 20px;
    font-size: 18px;
  }

  .score-card {
    margin: auto 14px 14px;
    padding: 16px;
  }

  .score-value {
    font-size: 40px;
  }
}

@media (max-width: 980px) {
  .app-frame {
    grid-template-columns: 1fr;
  }

  .sidebar {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    align-items: start;
    border-right: 0;
    border-bottom: 1px solid var(--line);
  }

  .brand-card {
    border-bottom: 0;
    padding: 18px 16px 8px;
  }

  .brand-card h1 {
    font-size: clamp(26px, 5vw, 34px);
  }

  .side-nav {
    grid-column: 1 / -1;
    display: flex;
    gap: 8px;
    overflow-x: auto;
    padding: 8px 12px 14px;
    border-top: 1px solid #d1d3df;
  }

  .nav-item {
    white-space: nowrap;
    border-left: 0;
    border: 2px solid transparent;
    border-radius: 999px;
    background: #e6e7f0;
    padding: 8px 14px;
    font-size: 16px;
  }

  .nav-item.router-link-exact-active {
    border-left-color: transparent;
    border-color: #f06e50;
    background: #efdfe3;
  }

  .score-card {
    margin: 14px 12px 0 0;
    padding: 14px;
    min-width: 150px;
  }

  .score-value {
    font-size: 34px;
    margin-top: 8px;
  }

  .score-sub,
  .score-tag {
    font-size: 12px;
  }

  .top-tabs a {
    font-size: 18px;
    padding: 14px 10px;
  }
}

@media (max-width: 720px) {
  .score-card {
    display: none;
  }

  .brand-card {
    padding-bottom: 10px;
  }

  .side-nav {
    border-top: 0;
    padding-top: 0;
  }
}
</style>
