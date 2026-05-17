<template>
  <nav class="bt-nav" @mouseleave="closeSubmenu">
    <div class="bt-nav-brand">
      <div class="bt-nav-logo">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/>
          <circle cx="12" cy="10" r="2.5"/>
        </svg>
      </div>
      <span class="bt-nav-wordmark"><em>Connect</em>Local</span>
    </div>

    <div class="bt-nav-links" role="navigation" aria-label="Main navigation">
      <RouterLink to="/home">Home</RouterLink>
      <RouterLink to="/discover">Events</RouterLink>
      <RouterLink to="/journey" >Journey</RouterLink>

      <div class="bt-nav-dropdown" @mouseenter="openSubmenu" @mouseleave="scheduleClose">
        <RouterLink
          to="/best-time"
          class="bt-nav-trigger"
          :class="{ 'is-active': isBestTimeRoute }"
          @click="closeSubmenu"
          @focus="openSubmenu"
        >
          Best Time
          <svg class="bt-nav-chevron" :class="{ open: submenuOpen }" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M6 9l6 6 6-6"/>
          </svg>
        </RouterLink>

        <div v-show="submenuOpen" class="bt-nav-submenu" @mouseenter="cancelClose" @mouseleave="scheduleClose">
          <RouterLink :to="{ path: '/best-time', hash: '#step-now' }" class="bt-nav-sub" @click="closeSubmenu">
            <span class="bt-nav-sub-icon mint">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            </span>
            <span class="bt-nav-sub-text">
              <span class="bt-nav-sub-label">Right now</span>
              <span class="bt-nav-sub-desc">Live score for your area</span>
            </span>
          </RouterLink>
          <RouterLink :to="{ path: '/best-time', hash: '#step-where' }" class="bt-nav-sub" @click="closeSubmenu">
            <span class="bt-nav-sub-icon green">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>
            </span>
            <span class="bt-nav-sub-text">
              <span class="bt-nav-sub-label">Where to go</span>
              <span class="bt-nav-sub-desc">Top outdoor spots ranked</span>
            </span>
          </RouterLink>
          <RouterLink :to="{ path: '/best-time', hash: '#step-when' }" class="bt-nav-sub" @click="closeSubmenu">
            <span class="bt-nav-sub-icon yellow">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>
            </span>
            <span class="bt-nav-sub-text">
              <span class="bt-nav-sub-label">When you go</span>
              <span class="bt-nav-sub-desc">Heatmap &amp; quiet windows</span>
            </span>
          </RouterLink>
          <RouterLink :to="{ path: '/best-time', hash: '#step-community' }" class="bt-nav-sub" @click="closeSubmenu">
            <span class="bt-nav-sub-icon purple">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
            </span>
            <span class="bt-nav-sub-text">
              <span class="bt-nav-sub-label">Stay connected</span>
              <span class="bt-nav-sub-desc">Welcoming community spaces</span>
            </span>
          </RouterLink>
        </div>
      </div>
    </div>

    <RouterLink to="/checkin" class="bt-nav-cta">
      Start Check-in
      <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M5 12h14M13 5l7 7-7 7"/>
      </svg>
    </RouterLink>
  </nav>
</template>

<script setup>
import { ref, computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

const submenuOpen = ref(false)
const route = useRoute()
let closeTimer = null

const isBestTimeRoute = computed(() => route.path === '/best-time')

function openSubmenu() { cancelClose(); submenuOpen.value = true }
function scheduleClose() { cancelClose(); closeTimer = setTimeout(() => { submenuOpen.value = false }, 200) }
function cancelClose() { if (closeTimer) { clearTimeout(closeTimer); closeTimer = null } }
function closeSubmenu() { cancelClose(); submenuOpen.value = false }
</script>

<style scoped>
.bt-nav {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 52px;
  background: rgba(242, 250, 240, 0.92);
  backdrop-filter: blur(18px);
  border-bottom: 1px solid rgba(29, 113, 105, 0.12);
  box-shadow: 0 1px 0 rgba(29,113,105,0.06);
}

.bt-nav-brand { display: flex; align-items: center; gap: 12px; }
.bt-nav-logo { width: 38px; height: 38px; border-radius: 50%; background: linear-gradient(135deg,#0a9b8a,#056b5e); color: white; display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 16px rgba(7,141,127,0.3); }
.bt-nav-wordmark { font-family: Georgia,serif; font-size: 20px; color: #1a2e1e; }
.bt-nav-wordmark em { color: #0a9b8a; font-style: italic; }

.bt-nav-links { display: flex; gap: 28px; align-items: center; }
.bt-nav-links > a { font-size: 15px; font-weight: 600; color: #3a5a3e; text-decoration: none; transition: color 0.2s; }
.bt-nav-links > a:hover, .bt-nav-links > a.router-link-active { color: #0a9b8a; }
.bt-nav-coming { font-size: 15px; font-weight: 600; color: #3a5a3e; cursor: default; }

.bt-nav-dropdown { position: relative; }
.bt-nav-trigger {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 15px; font-weight: 600; color: #3a5a3e;
  text-decoration: none; cursor: pointer;
  transition: color 0.2s;
}


.bt-nav-trigger .is-active::after {
  content: ''; position: absolute;     left: 33.5rem;
    right: 0rem; bottom: 34px; height: 2px;
}
.bt-nav-trigger:hover, .bt-nav-trigger.is-active, .bt-nav-trigger.router-link-active { color: #0a9b8a; }
.bt-nav-chevron { transition: transform 0.25s; }
.bt-nav-chevron.open { transform: rotate(180deg); }

.bt-nav-submenu {
  position: absolute; top: calc(100% + 14px); right: -8px;
  min-width: 280px;
  background: white; border: 1px solid rgba(29,113,105,0.12);
  border-radius: 16px; padding: 10px;
  box-shadow: 0 20px 50px rgba(0,0,0,0.12), 0 4px 12px rgba(0,0,0,0.04);
  display: flex; flex-direction: column; gap: 2px;
  animation: bt-sub-in 0.18s cubic-bezier(0.22,1,0.36,1);
}
.bt-nav-submenu::before {
  content: ''; position: absolute; top: -6px; right: 28px;
  width: 12px; height: 12px;
  background: white;
  border-top: 1px solid rgba(29,113,105,0.12);
  border-left: 1px solid rgba(29,113,105,0.12);
  transform: rotate(45deg);
}
@keyframes bt-sub-in { from { opacity: 0; transform: translateY(-6px); } to { opacity: 1; transform: none; } }

.bt-nav-sub {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 12px; border-radius: 10px;
  text-decoration: none; transition: background 0.15s;
}
.bt-nav-sub:hover { background: #f0faf0; }
.bt-nav-sub.router-link-exact-active { background: #e8f8f0; }
.bt-nav-sub-icon {
  width: 32px; height: 32px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.bt-nav-sub-icon.mint   { background: #d6f4e7; color: #1d7169; }
.bt-nav-sub-icon.green  { background: #e4f5e0; color: #0a9b8a; }
.bt-nav-sub-icon.yellow { background: #fff3c2; color: #b88a00; }
.bt-nav-sub-icon.purple { background: #e6dcff; color: #5b3fb6; }
.bt-nav-sub-text { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
.bt-nav-sub-label { font-family: Georgia,serif; font-size: 14px; font-weight: 700; color: #0f1e12; line-height: 1.2; }
.bt-nav-sub-desc { font-family: system-ui,sans-serif; font-size: 12px; color: #6a8e6e; font-weight: 500; }

.bt-nav-cta {
  display: inline-flex; align-items: center; gap: 8px;
  font-size: 14px; font-weight: 700; color: #0a9b8a;
  text-decoration: none; padding: 10px 22px;
  border: 1.5px solid #0a9b8a; border-radius: 999px;
  transition: all 0.3s;
}
.bt-nav-cta:hover { background: #0a9b8a; color: white; }

@media (max-width: 1000px) {
  .bt-nav { padding: 12px 20px; }
  .bt-nav-links { display: none; }
}
</style>