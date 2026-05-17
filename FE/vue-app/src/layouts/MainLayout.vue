<template>
  <div class="layout">
    <nav
      class="nav"
      :class="{
        scrolled: scrollY > 60,
        hidden: navHidden
      }"
    >
      <RouterLink to="/home" class="nav-brand">
        <div class="nav-logo">
          <svg
            viewBox="0 0 24 24"
            width="18"
            height="18"
            fill="none"
            stroke="currentColor"
            stroke-width="2.2"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z" />
            <circle cx="12" cy="10" r="2.5" />
          </svg>
        </div>

        <span class="nav-wordmark"><em>Connect</em>Local</span>
      </RouterLink>

      <button
        class="menu-toggle"
        type="button"
        @click="menuOpen = !menuOpen"
        aria-label="Toggle navigation menu"
      >
        ☰
      </button>

      <div
        class="nav-links"
        :class="{ open: menuOpen }"
        role="navigation"
        aria-label="Main navigation"
      >
        <RouterLink to="/home" @click="menuOpen = false">Home</RouterLink>
        <RouterLink to="/discover" @click="menuOpen = false">Events</RouterLink>
        <RouterLink to="/journey" @click="menuOpen = false">Journey</RouterLink>
        <RouterLink to="/best-time" @click="menuOpen = false">Best Time</RouterLink>
        <RouterLink to="/suburb-explorer" class="item">Suburb Explorer</RouterLink>
      </div>

      <div class="nav-actions">
        <RouterLink to="/checkin-form" class="start-link">
          Start Check-in
          <span>→</span>
        </RouterLink>

        <label class="text-scale">
          <span class="a-small">A</span>
          <input
            type="range"
            min="75"
            max="125"
            step="5"
            v-model.number="textScale"
            aria-label="Adjust text size"
          />
          <span class="a-large">A</span>
          <span class="scale-pct">{{ textScale }}%</span>
        </label>
      </div>
    </nav>

    <main class="layout-main">
      <slot />
    </main>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { uiStore } from '../stores/uiStore'

const scrollY = ref(0)
const lastScrollY = ref(0)
const navHidden = ref(false)
const menuOpen = ref(false)
const textScale = ref(uiStore.textScale || 100)

function handleScroll() {
  const currentY = window.scrollY

  if (currentY <= 20) {
    navHidden.value = false
  } else if (currentY > lastScrollY.value && !menuOpen.value) {
    navHidden.value = true
  } else if (currentY < lastScrollY.value) {
    navHidden.value = false
  }

  scrollY.value = currentY
  lastScrollY.value = currentY
}

watch(
  textScale,
  (value) => {
    uiStore.textScale = value
    document.documentElement.style.setProperty('--font-scale', value / 100)
  },
  { immediate: true }
)

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.layout {
  min-height: 100vh;
  background: #f2faf0;
}

.nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 28px;
  padding: 14px 52px;
  background: rgba(242, 250, 240, 0.9);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(29, 113, 105, 0.1);
  transition: transform 0.35s ease, background 0.35s ease, padding 0.35s ease, box-shadow 0.35s ease;
}

.nav.scrolled {
  background: rgba(242, 250, 240, 0.95);
  padding: 10px 52px;
  box-shadow: 0 1px 0 rgba(29, 113, 105, 0.12);
}

.nav.hidden {
  /* transform: translateY(-100%); */
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  flex-shrink: 0;
}

.nav-logo {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0a9b8a, #056b5e);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 16px rgba(7, 141, 127, 0.3);
}

.nav-wordmark {
  font-family: Georgia, serif;
  font-size: 20px;
  color: #1a2e1e;
}

.nav-wordmark em {
  color: #0a9b8a;
  font-style: italic;
}

.nav-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 32px;
  flex: 1;
}

.nav-links a {
  font-size: 15px;
  font-weight: 600;
  color: #3a5a3e;
  text-decoration: none;
  transition: color 0.2s;
  white-space: nowrap;
}

.nav-links a:hover,
.nav-links .router-link-active {
  color: #0a9b8a;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-shrink: 0;
}

.start-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 20px;
  border: 1.5px solid #0a9b8a;
  border-radius: 999px;
  color: #0a9b8a;
  text-decoration: none;
  font-size: 14px;
  font-weight: 700;
  transition: all 0.3s;
  white-space: nowrap;
}

.start-link:hover {
  background: #0a9b8a;
  color: white;
}

.text-scale {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px;
  border: 1px solid rgba(29, 113, 105, 0.16);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
}

.a-small {
  font-family: Georgia, serif;
  font-size: 13px;
  font-weight: 700;
  color: #0a9b8a;
  line-height: 1;
}

.a-large {
  font-family: Georgia, serif;
  font-size: 20px;
  font-weight: 700;
  color: #0a9b8a;
  line-height: 1;
}

.text-scale input {
  width: 82px;
  accent-color: #0a9b8a;
}

.scale-pct {
  font-size: 12px;
  font-weight: 700;
  color: #6a8e6e;
  min-width: 34px;
}

.menu-toggle {
  display: none;
  border: none;
  background: #0a9b8a;
  color: white;
  border-radius: 10px;
  padding: 8px 12px;
  font-size: 20px;
  cursor: pointer;
}

.layout-main {
  min-height: 100vh;
  padding-top: 64px;
}

@media (max-width: 1100px) {
  .text-scale {
    display: none;
  }
}

@media (max-width: 900px) {
  .nav {
    padding: 14px 20px;
    flex-wrap: wrap;
  }

  .nav.scrolled {
    padding: 12px 20px;
  }

  .menu-toggle {
    display: block;
  }

  .nav-links {
    display: none;
    width: 100%;
    flex-direction: column;
    align-items: flex-start;
    gap: 14px;
    padding-top: 14px;
  }

  .nav-links.open {
    display: flex;
  }

  .nav-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .start-link {
    padding: 8px 18px;
  }

  .layout-main {
    padding-top: 64px;
  }
}

@media (max-width: 600px) {
  .nav-brand {
    gap: 10px;
  }

  .nav-logo {
    width: 34px;
    height: 34px;
  }

  .nav-wordmark {
    font-size: 18px;
  }
}
</style>