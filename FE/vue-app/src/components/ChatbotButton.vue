<!--
  ChatbotButton.vue — v4.4
  ─────────────────────────────────────────────────────────────────────────────
  Fix in this version:
    • Radial menu no longer flickers when moving from the main chatbot button
      to the small radial icons.
    • Mouse leave now uses a short grace delay instead of closing instantly.
    • Radial items also keep the menu open when hovered.
    • Pending close timers are cleared on click and unmount.
-->
<template>
  <!-- Hide on routes that shouldn't have the chatbot (login, etc) -->
  <template v-if="shouldShow">
    <!-- ════════════════════════════════════════════════════════════════════
         FLOATING ASSISTANT (closed state) — FAB + radial menu
         ════════════════════════════════════════════════════════════════ -->
    <div
      v-if="!chatbotStore.isOpen"
      class="cl-fab-cluster"
      @mouseenter="onFabHover(true)"
      @mouseleave="onFabHover(false)"
    >
      <!-- ─── Radial action items (fan out on hover) ────────────────────── -->
      <button
        v-for="(item, idx) in radialItems"
        :key="item.id"
        class="cl-radial-item"
        :class="{ 'is-open': radialOpen }"
        :style="getRadialStyle(idx, radialItems.length)"
        :aria-label="item.label"
        :title="item.label"
        @mouseenter="onFabHover(true)"
        @mouseleave="onFabHover(false)"
        @click="onRadialClick(item)"
      >
        <span class="cl-radial-icon" v-html="item.svg"></span>
        <span class="cl-radial-tooltip">{{ item.label }}</span>
      </button>

      <!-- ─── Main FAB with bot face ───────────────────────────────────── -->
      <button
        class="cl-fab"
        :class="{ 'has-unread': chatbotStore.hasUnread, 'is-hovered': radialOpen }"
        @click="onFabClick"
        aria-label="Open ConnectLocal assistant"
      >
        <!-- Outer pulse rings -->
        <span class="cl-fab-pulse" aria-hidden="true"></span>
        <span class="cl-fab-pulse cl-fab-pulse-delay" aria-hidden="true"></span>

        <!-- Inner gradient circle with bot face -->
        <span class="cl-fab-inner">
          <svg
            viewBox="0 0 32 32"
            width="34"
            height="34"
            fill="none"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <!-- Antenna -->
            <path d="M16 5v3" />
            <circle cx="16" cy="4" r="1.2" fill="currentColor" stroke="none" />
            <!-- Head -->
            <rect x="6.5" y="9" width="19" height="16" rx="4.5" />
            <!-- Eyes -->
            <circle cx="12" cy="16.5" r="1.4" fill="currentColor" stroke="none" />
            <circle cx="20" cy="16.5" r="1.4" fill="currentColor" stroke="none" />
            <!-- Smile -->
            <path d="M13 20.5c.8 1 1.8 1.5 3 1.5s2.2-.5 3-1.5" />
            <!-- Side ears -->
            <path d="M6.5 14.5h-1.5M27 14.5h-1.5" />
          </svg>
        </span>

        <!-- Unread indicator dot -->
        <span v-if="chatbotStore.hasUnread" class="cl-unread-dot" aria-hidden="true"></span>
      </button>

      <!-- First-time hint -->
      <transition name="cl-hint">
        <div v-if="showHint" class="cl-fab-hint" aria-hidden="true">
          Need help? <strong>Ask me anything</strong>
        </div>
      </transition>
    </div>

    <!-- ════════════════════════════════════════════════════════════════════
         CHAT PANEL (open state) — large right-side
         ════════════════════════════════════════════════════════════════ -->
    <transition name="cl-panel">
      <aside
        v-if="chatbotStore.isOpen"
        class="cl-panel"
        :style="{ '--cl-font-scale': fontScale }"
        role="dialog"
        aria-label="ConnectLocal assistant"
      >
        <!-- ─── Header ────────────────────────────────────────────────── -->
        <header class="cl-header">
          <div class="cl-header-left">
            <div class="cl-header-avatar">
              <svg
                viewBox="0 0 32 32"
                width="22"
                height="22"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M16 5v3" />
                <circle cx="16" cy="4" r="1.2" fill="currentColor" stroke="none" />
                <rect x="6.5" y="9" width="19" height="16" rx="4.5" />
                <circle cx="12" cy="16.5" r="1.4" fill="currentColor" stroke="none" />
                <circle cx="20" cy="16.5" r="1.4" fill="currentColor" stroke="none" />
                <path d="M13 20.5c.8 1 1.8 1.5 3 1.5s2.2-.5 3-1.5" />
              </svg>
              <span class="cl-online-dot" aria-hidden="true"></span>
            </div>

            <div class="cl-header-text">
              <span class="cl-header-title"><em>Connect</em>Local Guide</span>
              <span class="cl-header-status">
                <span class="cl-status-dot"></span> Online · Ready to help
              </span>
            </div>
          </div>

          <div class="cl-header-right">
            <div class="cl-font-slider" role="group" aria-label="Text size">
              <span class="cl-font-label cl-font-small">A</span>
              <input
                v-model.number="fontScalePct"
                type="range"
                :min="90"
                :max="140"
                :step="5"
                class="cl-slider"
                aria-label="Text size"
              />
              <span class="cl-font-label cl-font-big">A</span>
              <span class="cl-font-value">{{ fontScalePct }}%</span>
            </div>

            <button class="cl-header-close" @click="chatbotStore.close()" aria-label="Close and reset">
              <svg
                viewBox="0 0 24 24"
                width="22"
                height="22"
                fill="none"
                stroke="currentColor"
                stroke-width="2.2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M18 6 6 18M6 6l12 12" />
              </svg>
            </button>
          </div>
        </header>

        <!-- ─── Thread ────────────────────────────────────────────────── -->
        <div ref="threadEl" class="cl-thread">
          <transition-group name="cl-msg" tag="div" class="cl-msg-list">
            <!-- Welcome message — always first when no other messages yet -->
            <div v-if="!chatbotStore.messages.length" key="welcome" class="cl-msg assistant">
              <div class="cl-msg-avatar">
                <svg
                  viewBox="0 0 32 32"
                  width="16"
                  height="16"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <rect x="6.5" y="9" width="19" height="16" rx="4.5" />
                  <circle cx="12" cy="16.5" r="1.4" fill="currentColor" stroke="none" />
                  <circle cx="20" cy="16.5" r="1.4" fill="currentColor" stroke="none" />
                  <path d="M13 20.5c.8 1 1.8 1.5 3 1.5s2.2-.5 3-1.5" />
                </svg>
              </div>

              <div class="cl-msg-bubble">
                <p>👋 Hi! I'm your <em>ConnectLocal</em> guide.</p>
                <p>I can help you find activities, plan a journey, or explain anything on the site.</p>
                <p class="cl-msg-prompt">What would you like to do today?</p>
              </div>
            </div>

            <div
              v-for="msg in chatbotStore.messages"
              :key="msg.id"
              class="cl-msg"
              :class="msg.role"
            >
              <div v-if="msg.role === 'assistant'" class="cl-msg-avatar">
                <svg
                  viewBox="0 0 32 32"
                  width="16"
                  height="16"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <rect x="6.5" y="9" width="19" height="16" rx="4.5" />
                  <circle cx="12" cy="16.5" r="1.4" fill="currentColor" stroke="none" />
                  <circle cx="20" cy="16.5" r="1.4" fill="currentColor" stroke="none" />
                  <path d="M13 20.5c.8 1 1.8 1.5 3 1.5s2.2-.5 3-1.5" />
                </svg>
              </div>

              <div class="cl-msg-bubble">{{ msg.content }}</div>
            </div>

            <!-- Typing indicator -->
            <div v-if="chatbotStore.isLoading" key="loading" class="cl-msg assistant">
              <div class="cl-msg-avatar">
                <svg
                  viewBox="0 0 32 32"
                  width="16"
                  height="16"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <rect x="6.5" y="9" width="19" height="16" rx="4.5" />
                  <circle cx="12" cy="16.5" r="1.4" fill="currentColor" stroke="none" />
                  <circle cx="20" cy="16.5" r="1.4" fill="currentColor" stroke="none" />
                </svg>
              </div>

              <div class="cl-msg-bubble cl-typing">
                <span class="cl-typing-dot"></span>
                <span class="cl-typing-dot"></span>
                <span class="cl-typing-dot"></span>
              </div>
            </div>

            <!-- Action confirmation card -->
            <div v-if="chatbotStore.pendingAction" key="pending" class="cl-action-card">
              <div class="cl-action-icon">
                <svg
                  viewBox="0 0 24 24"
                  width="18"
                  height="18"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2.2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M12 9v4M12 17h.01M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                </svg>
              </div>

              <p class="cl-action-text">{{ describePendingAction(chatbotStore.pendingAction) }}</p>

              <div class="cl-action-buttons">
                <button class="cl-btn-secondary" @click="cancelAction()">Cancel</button>
                <button class="cl-btn-primary" @click="approveAction()">Allow</button>
              </div>
            </div>
          </transition-group>
        </div>

        <!-- ─── Suggested prompts (only when empty) ─────────────────── -->
        <div v-if="!chatbotStore.messages.length && !chatbotStore.isLoading" class="cl-suggestions">
          <button
            v-for="prompt in displayedSuggestions"
            :key="prompt"
            class="cl-suggestion-chip"
            @click="useSuggestion(prompt)"
          >
            {{ prompt }} →
          </button>
        </div>

        <!-- ─── Input bar ───────────────────────────────────────────── -->
        <form class="cl-input-bar" @submit.prevent="handleSubmit">
          <input
            ref="inputEl"
            v-model="inputText"
            type="text"
            placeholder="Ask me anything..."
            :disabled="chatbotStore.isLoading"
            aria-label="Message"
            autocomplete="off"
          />

          <button
            type="submit"
            class="cl-send-btn"
            :disabled="!inputText.trim() || chatbotStore.isLoading"
            aria-label="Send"
          >
            <svg
              viewBox="0 0 24 24"
              width="20"
              height="20"
              fill="none"
              stroke="currentColor"
              stroke-width="2.4"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M5 12h14M13 5l7 7-7 7" />
            </svg>
          </button>
        </form>

        <!-- Privacy footer -->
        <div class="cl-privacy-note">
          <svg
            viewBox="0 0 24 24"
            width="12"
            height="12"
            fill="none"
            stroke="currentColor"
            stroke-width="2.2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <rect width="18" height="11" x="3" y="11" rx="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
          Your conversation is private and resets when you close this window
        </div>
      </aside>
    </transition>
  </template>
</template>

<script setup>
import { ref, computed, nextTick, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { chatbotStore } from '../stores/chatbotStore'
import { useChatbot } from '../composables/useChatbot'

const { sendMessage, approveAction, cancelAction } = useChatbot()
const route = useRoute()

// ─── State ──────────────────────────────────────────────────────────────────
const inputText = ref('')
const inputEl = ref(null)
const threadEl = ref(null)
const radialOpen = ref(false)
const showHint = ref(false)
const fontScalePct = ref(100)
const fontScale = computed(() => fontScalePct.value / 100)

// ─── Radial hover close delay ───────────────────────────────────────────────
// Prevent flicker when moving the cursor from the main FAB to the radial icons.
const RADIAL_CLOSE_DELAY = 180
let radialCloseTimer = null

function clearRadialCloseTimer() {
  if (!radialCloseTimer) return
  clearTimeout(radialCloseTimer)
  radialCloseTimer = null
}

// ─── Per-route visibility ───────────────────────────────────────────────────
// Hide the chatbot on routes where it doesn't make sense (login, etc).
const HIDDEN_ROUTES = ['/login']

const shouldShow = computed(() => {
  const path = route?.path || ''
  return !HIDDEN_ROUTES.some(r => path.startsWith(r))
})

// ─── Radial quick-action items ──────────────────────────────────────────────
const radialItems = [
  {
    id: 'events',
    label: 'Find events',
    prompt: 'Find free events near me this week',
    svg: '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>',
  },
  {
    id: 'journey',
    label: 'Plan a journey',
    prompt: 'Help me plan a journey',
    svg: '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 0-8-3-8-7s3-7 8-7h6c5 0 8 3 8 7s-3 7-8 7"/><path d="M3 12h18"/><circle cx="6" cy="12" r="1"/><circle cx="18" cy="12" r="1"/></svg>',
  },
  {
    id: 'besttime',
    label: 'Best time to go',
    prompt: 'When is the best time to go out?',
    svg: '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>',
  },
  {
    id: 'checkin',
    label: 'Wellbeing check-in',
    prompt: 'I want to do the wellbeing check-in',
    svg: '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>',
  },
]

const displayedSuggestions = computed(() => {
  if (chatbotStore.suggestedPrompts.length) return chatbotStore.suggestedPrompts
  return radialItems.map(i => i.prompt)
})

// ─── Radial positioning math ────────────────────────────────────────────────
function getRadialStyle(index, total) {
  const radius = 108
  const startDeg = -175
  const endDeg = -95
  const step = total > 1 ? (endDeg - startDeg) / (total - 1) : 0
  const deg = startDeg + step * index
  const rad = (deg * Math.PI) / 180
  const x = Math.cos(rad) * radius
  const y = Math.sin(rad) * radius

  return {
    '--cl-radial-x': `${x}px`,
    '--cl-radial-y': `${y}px`,
    '--cl-radial-delay': `${index * 35}ms`,
  }
}

// ─── Behaviour ──────────────────────────────────────────────────────────────
function onFabHover(isHovering) {
  if (isHovering) {
    clearRadialCloseTimer()
    radialOpen.value = true
    showHint.value = false
    return
  }

  clearRadialCloseTimer()

  radialCloseTimer = setTimeout(() => {
    radialOpen.value = false
    radialCloseTimer = null
  }, RADIAL_CLOSE_DELAY)
}

function onFabClick() {
  clearRadialCloseTimer()
  radialOpen.value = false
  chatbotStore.toggle()
}

function onRadialClick(item) {
  clearRadialCloseTimer()
  radialOpen.value = false
  chatbotStore.open()

  nextTick(() => {
    sendMessage(item.prompt)
  })
}

async function handleSubmit() {
  const text = inputText.value.trim()
  if (!text) return

  inputText.value = ''
  await sendMessage(text)
}

function useSuggestion(prompt) {
  inputText.value = prompt
  handleSubmit()
}

// Auto-scroll
watch(
  () => [chatbotStore.messages.length, chatbotStore.isLoading, chatbotStore.pendingAction],
  () => {
    nextTick(() => {
      if (threadEl.value) {
        threadEl.value.scrollTop = threadEl.value.scrollHeight
      }
    })
  }
)

// Focus input on open
watch(() => chatbotStore.isOpen, (open) => {
  radialOpen.value = false
  clearRadialCloseTimer()

  if (open) {
    chatbotStore.setSuggestionsForRoute(route.path)
    nextTick(() => inputEl.value?.focus())
    inputText.value = ''
  }
})

// Refresh suggestions if the user navigates while the panel is open.
watch(() => route.path, (newPath) => {
  if (chatbotStore.isOpen) {
    chatbotStore.setSuggestionsForRoute(newPath)
  }
})

// ESC closes the panel
function onKey(e) {
  if (e.key === 'Escape' && chatbotStore.isOpen) chatbotStore.close()
}

// Show hint after 1.2s, dismiss after 8s
let hintTimeout1 = null
let hintTimeout2 = null

onMounted(() => {
  window.addEventListener('keydown', onKey)
  hintTimeout1 = setTimeout(() => { showHint.value = true }, 1200)
  hintTimeout2 = setTimeout(() => { showHint.value = false }, 8000)
  chatbotStore.setSuggestionsForRoute(route.path)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  clearTimeout(hintTimeout1)
  clearTimeout(hintTimeout2)
  clearRadialCloseTimer()
})

// ─── Pending-action description ─────────────────────────────────────────────
function describePendingAction(action) {
  if (!action) return ''

  const { name, args = {} } = action

  switch (name) {
    case 'navigate_to':
      return `I'd like to take you to ${describeRoute(args.route)}. Allow?`

    case 'search_events': {
      const parts = []
      if (args.is_free) parts.push('free')
      if (args.category) parts.push(args.category)
      parts.push('events')
      if (args.suburb) parts.push(`in ${args.suburb}`)
      if (args.this_week_only) parts.push('this week')
      return `I'd like to search for ${parts.join(' ')}. Allow?`
    }

    case 'plan_journey': {
      const to = args.to_place || 'your destination'
      const from = args.from_place ? ` from ${args.from_place}` : ''
      const at = args.arrive_by ? ` arriving by ${args.arrive_by}` : ''
      return `I'd like to plan a journey${from} to ${to}${at}. Allow?`
    }

    case 'start_checkin':
      return `I'd like to take you to the wellbeing check-in. Allow?`

    case 'check_best_time':
      return `I'd like to show you the ${args.scope === 'week' ? 'weekly' : 'live'} best-time view. Allow?`

    case 'find_welcoming_places':
      return `I'd like to show you welcoming places${args.suburb ? ` near ${args.suburb}` : ''}. Allow?`

    case 'find_open_spaces':
      return `I'd like to show you outdoor spaces${args.with_toilets ? ' with toilets' : ''}${args.suburb ? ` near ${args.suburb}` : ''}. Allow?`

    default:
      return "I'd like to take an action for you. Allow?"
  }
}

function describeRoute(route) {
  const labels = {
    '/home': 'the home page',
    '/discover': 'the events page',
    '/journey': 'the journey planner',
    '/checkin': 'the wellbeing check-in',
    '/checkin/form': 'the check-in form',
    '/results': 'your results page',
    '/best-time': 'the Best Time page',
    '/best-time/now': 'the live Best Time view',
    '/best-time/week': 'the weekly Best Time view',
    '/welcoming-spaces': 'welcoming spaces',
    '/resources': 'support resources',
    '/about': 'the about page',
  }

  return labels[route] || `the ${route} page`
}
</script>

<style scoped>
/* ════════════════════════════════════════════════════════════════════════════
   FAB CLUSTER (FAB + radial items + hint)
   ════════════════════════════════════════════════════════════════════════ */
.cl-fab-cluster {
  position: fixed;
  bottom: 32px;
  right: 32px;
  z-index: 9998;
  width: 230px;
  height: 230px;
  pointer-events: none;
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
}

/* ─── Radial items ──────────────────────────────────────────────────────── */
.cl-radial-item {
  pointer-events: auto;
  position: absolute;
  bottom: 22px;
  right: 22px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.97);
  color: #0a9b8a;
  box-shadow: 0 10px 26px rgba(7, 141, 127, 0.2), 0 3px 8px rgba(0, 0, 0, 0.07);
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translate(0, 0) scale(0);
  opacity: 0;
  will-change: transform, opacity, box-shadow;
  backface-visibility: hidden;
  transition:
    transform 0.42s cubic-bezier(0.34, 1.56, 0.64, 1),
    opacity 0.28s ease-out,
    background 0.28s ease,
    color 0.28s ease,
    box-shadow 0.28s ease;
  transition-delay: 0ms;
}

.cl-radial-item.is-open {
  transform: translate(var(--cl-radial-x), var(--cl-radial-y)) scale(1);
  opacity: 1;
  transition-delay: var(--cl-radial-delay);
}

.cl-radial-item:hover {
  background: linear-gradient(135deg, #0a9b8a, #056b5e);
  color: white;
  box-shadow: 0 12px 32px rgba(7, 141, 127, 0.45);
}

.cl-radial-tooltip {
  position: absolute;
  right: 72px;
  top: 50%;
  transform: translateY(-50%);
  font-family: system-ui, sans-serif;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  color: #1a2e1e;
  background: white;
  padding: 8px 14px;
  border-radius: 999px;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.1);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.18s 0.05s;
}

.cl-radial-item:hover .cl-radial-tooltip {
  opacity: 1;
}

/* ─── Main FAB ──────────────────────────────────────────────────────────── */
.cl-fab {
  pointer-events: auto;
  position: relative;
  width: 76px;
  height: 76px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  background: transparent;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  filter: drop-shadow(0 18px 36px rgba(7, 141, 127, 0.42));
}

.cl-fab:hover,
.cl-fab.is-hovered {
  transform: translateY(-5px);
}

.cl-fab:active {
  transform: translateY(-1px);
}

.cl-fab:focus-visible {
  outline: 3px solid rgba(10, 155, 138, 0.5);
  outline-offset: 4px;
  border-radius: 50%;
}

.cl-fab-inner {
  position: relative;
  z-index: 2;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: linear-gradient(135deg, #0a9b8a 0%, #056b5e 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow:
    inset 0 -3px 8px rgba(0, 0, 0, 0.18),
    inset 0 2px 4px rgba(255, 255, 255, 0.28);
}

/* Pulse rings */
.cl-fab-pulse {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: rgba(10, 155, 138, 0.34);
  animation: cl-pulse 2.6s ease-out infinite;
  z-index: 1;
}

.cl-fab-pulse-delay {
  animation-delay: 1.3s;
}

@keyframes cl-pulse {
  0% {
    transform: scale(1);
    opacity: 0.55;
  }

  80% {
    transform: scale(1.65);
    opacity: 0;
  }

  100% {
    transform: scale(1.65);
    opacity: 0;
  }
}

.cl-unread-dot {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #ffb48c;
  box-shadow: 0 0 0 3px white;
  z-index: 3;
  animation: cl-blink 1.6s ease-in-out infinite;
}

@keyframes cl-blink {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }

  50% {
    opacity: 0.6;
    transform: scale(0.85);
  }
}

/* ─── Hint ──────────────────────────────────────────────────────────────── */
.cl-fab-hint {
  pointer-events: none;
  position: absolute;
  bottom: 92px;
  right: 0;
  font-family: system-ui, sans-serif;
  font-size: 14px;
  color: #1a2e1e;
  background: white;
  padding: 11px 18px;
  border-radius: 14px;
  box-shadow: 0 8px 26px rgba(7, 141, 127, 0.18);
  white-space: nowrap;
}

.cl-fab-hint strong {
  color: #0a9b8a;
}

.cl-fab-hint::after {
  content: '';
  position: absolute;
  bottom: -6px;
  right: 28px;
  width: 12px;
  height: 12px;
  background: white;
  transform: rotate(45deg);
  box-shadow: 4px 4px 8px rgba(7, 141, 127, 0.08);
}

.cl-hint-enter-active,
.cl-hint-leave-active {
  transition: opacity 0.4s, transform 0.4s;
}

.cl-hint-enter-from,
.cl-hint-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

/* ════════════════════════════════════════════════════════════════════════════
   CHAT PANEL
   ════════════════════════════════════════════════════════════════════════ */
.cl-panel {
  position: fixed;
  top: 24px;
  bottom: 24px;
  right: 24px;
  width: 520px;
  max-width: calc(100vw - 48px);
  z-index: 9999;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid rgba(29, 113, 105, 0.16);
  border-radius: 24px;
  box-shadow:
    0 32px 80px rgba(7, 141, 127, 0.22),
    0 4px 12px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: system-ui, -apple-system, sans-serif;
  color: #1a2e1e;
  --cl-font-scale: 1;
  font-size: calc(15px * var(--cl-font-scale));
}

.cl-panel-enter-active {
  transition: transform 0.42s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.3s;
}

.cl-panel-leave-active {
  transition: transform 0.28s ease-in, opacity 0.22s;
}

.cl-panel-enter-from,
.cl-panel-leave-to {
  opacity: 0;
  transform: translateX(40px) scale(0.97);
}

/* ─── Header ────────────────────────────────────────────────────────────── */
.cl-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 20px 22px;
  border-bottom: 1px solid rgba(29, 113, 105, 0.08);
  background: linear-gradient(180deg, rgba(242, 250, 240, 0.6) 0%, transparent 100%);
}

.cl-header-left {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.cl-header-avatar {
  position: relative;
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0a9b8a, #056b5e);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 14px rgba(7, 141, 127, 0.32);
  flex-shrink: 0;
}

.cl-online-dot {
  position: absolute;
  bottom: -1px;
  right: -1px;
  width: 13px;
  height: 13px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 0 2px white;
}

.cl-header-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.cl-header-title {
  font-family: Georgia, serif;
  font-size: calc(18px * var(--cl-font-scale));
  color: #1a2e1e;
  line-height: 1.2;
}

.cl-header-title em {
  color: #0a9b8a;
  font-style: italic;
}

.cl-header-status {
  font-size: calc(12px * var(--cl-font-scale));
  color: #4a6a4e;
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.cl-status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #22c55e;
  display: inline-block;
}

.cl-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.cl-font-slider {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 13px;
  background: rgba(10, 155, 138, 0.08);
  border-radius: 999px;
}

.cl-font-label {
  font-family: Georgia, serif;
  color: #4a6a4e;
  line-height: 1;
}

.cl-font-small {
  font-size: 11px;
}

.cl-font-big {
  font-size: 15px;
}

.cl-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 70px;
  height: 4px;
  border-radius: 2px;
  background: rgba(10, 155, 138, 0.25);
  outline: none;
  cursor: pointer;
}

.cl-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 15px;
  height: 15px;
  border-radius: 50%;
  background: #0a9b8a;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(7, 141, 127, 0.4);
}

.cl-slider::-moz-range-thumb {
  width: 15px;
  height: 15px;
  border-radius: 50%;
  background: #0a9b8a;
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 4px rgba(7, 141, 127, 0.4);
}

.cl-font-value {
  font-size: 11px;
  font-weight: 700;
  color: #0a9b8a;
  min-width: 30px;
}

.cl-header-close {
  background: none;
  border: none;
  cursor: pointer;
  color: #6a8e6e;
  padding: 7px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, color 0.2s;
}

.cl-header-close:hover {
  background: rgba(10, 155, 138, 0.1);
  color: #0a9b8a;
}

/* ─── Thread ────────────────────────────────────────────────────────────── */
.cl-thread {
  flex: 1;
  overflow-y: auto;
  padding: 22px;
  scroll-behavior: smooth;
}

.cl-thread::-webkit-scrollbar {
  width: 6px;
}

.cl-thread::-webkit-scrollbar-thumb {
  background: rgba(10, 155, 138, 0.25);
  border-radius: 6px;
}

.cl-msg-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.cl-msg-enter-active {
  transition: opacity 0.32s, transform 0.32s cubic-bezier(0.22, 1, 0.36, 1);
}

.cl-msg-leave-active {
  transition: opacity 0.22s, transform 0.22s;
}

.cl-msg-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.cl-msg-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.cl-msg {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.cl-msg.user {
  flex-direction: row-reverse;
}

.cl-msg-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0a9b8a, #056b5e);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 3px 8px rgba(7, 141, 127, 0.25);
}

.cl-msg-bubble {
  max-width: 78%;
  padding: 14px 18px;
  border-radius: 18px;
  font-size: calc(15px * var(--cl-font-scale));
  line-height: 1.55;
  word-wrap: break-word;
}

.cl-msg-bubble p {
  margin: 0 0 7px;
}

.cl-msg-bubble p:last-child {
  margin-bottom: 0;
}

.cl-msg-bubble em {
  font-style: italic;
  color: #0a9b8a;
  font-weight: 600;
}

.cl-msg-prompt {
  font-weight: 600;
  color: #1a2e1e;
  margin-top: 10px !important;
}

.cl-msg.assistant .cl-msg-bubble {
  background: linear-gradient(180deg, #f0faed 0%, #e6f5e2 100%);
  color: #1a2e1e;
  border: 1px solid rgba(29, 113, 105, 0.1);
  border-bottom-left-radius: 6px;
}

.cl-msg.user .cl-msg-bubble {
  background: linear-gradient(135deg, #0a9b8a, #056b5e);
  color: white;
  border-bottom-right-radius: 6px;
  box-shadow: 0 4px 12px rgba(7, 141, 127, 0.22);
}

.cl-typing {
  display: flex;
  gap: 5px;
  padding: 16px 20px;
}

.cl-typing-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: #0a9b8a;
  opacity: 0.5;
  animation: cl-typing 1.3s infinite ease-in-out;
}

.cl-typing-dot:nth-child(2) {
  animation-delay: 0.16s;
}

.cl-typing-dot:nth-child(3) {
  animation-delay: 0.32s;
}

@keyframes cl-typing {
  0%,
  80%,
  100% {
    transform: scale(0.6);
    opacity: 0.4;
  }

  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* ─── Action card ──────────────────────────────────────────────────────── */
.cl-action-card {
  margin-top: 4px;
  background: linear-gradient(135deg, #fef6ed 0%, #fdebd6 100%);
  border: 1.5px solid rgba(255, 180, 140, 0.6);
  border-radius: 16px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  box-shadow: 0 4px 14px rgba(255, 180, 140, 0.18);
}

.cl-action-icon {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #c66b32;
  font-weight: 700;
  font-size: calc(11.5px * var(--cl-font-scale));
  text-transform: uppercase;
  letter-spacing: 1.5px;
}

.cl-action-icon::after {
  content: 'Confirm action';
}

.cl-action-text {
  font-size: calc(15px * var(--cl-font-scale));
  color: #5b3a1c;
  line-height: 1.5;
  margin: 0;
}

.cl-action-buttons {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.cl-btn-primary,
.cl-btn-secondary {
  font-family: system-ui, sans-serif;
  font-size: calc(14px * var(--cl-font-scale));
  font-weight: 700;
  padding: 10px 24px;
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.2s;
}

.cl-btn-secondary {
  background: white;
  border: 1.5px solid #cbb5a2;
  color: #6a4f33;
}

.cl-btn-secondary:hover {
  background: #faf3eb;
}

.cl-btn-primary {
  background: linear-gradient(135deg, #0a9b8a, #056b5e);
  border: none;
  color: white;
  box-shadow: 0 4px 12px rgba(7, 141, 127, 0.3);
}

.cl-btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(7, 141, 127, 0.42);
}

/* ─── Suggestions ──────────────────────────────────────────────────────── */
.cl-suggestions {
  display: flex;
  flex-direction: column;
  gap: 9px;
  padding: 8px 22px 12px;
}

.cl-suggestion-chip {
  font-family: system-ui, sans-serif;
  font-size: calc(14px * var(--cl-font-scale));
  font-weight: 600;
  color: #0a9b8a;
  background: white;
  border: 1.5px solid rgba(10, 155, 138, 0.32);
  border-radius: 14px;
  padding: 13px 18px;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}

.cl-suggestion-chip:hover {
  background: rgba(10, 155, 138, 0.06);
  border-color: #0a9b8a;
  transform: translateX(2px);
}

/* ─── Input ────────────────────────────────────────────────────────────── */
.cl-input-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid rgba(29, 113, 105, 0.08);
}

.cl-input-bar input {
  flex: 1;
  font-family: system-ui, sans-serif;
  font-size: calc(15px * var(--cl-font-scale));
  padding: 13px 20px;
  border: 1.5px solid rgba(29, 113, 105, 0.18);
  border-radius: 999px;
  outline: none;
  color: #1a2e1e;
  background: white;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.cl-input-bar input:focus {
  border-color: #0a9b8a;
  box-shadow: 0 0 0 3px rgba(10, 155, 138, 0.18);
}

.cl-input-bar input:disabled {
  opacity: 0.6;
}

.cl-input-bar input::placeholder {
  color: #94a8a4;
}

.cl-send-btn {
  width: 46px;
  height: 46px;
  flex-shrink: 0;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #0a9b8a, #056b5e);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(7, 141, 127, 0.32);
  transition: transform 0.2s, opacity 0.2s, box-shadow 0.2s;
}

.cl-send-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(7, 141, 127, 0.42);
}

.cl-send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* ─── Privacy ──────────────────────────────────────────────────────────── */
.cl-privacy-note {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 7px 0 14px;
  font-size: calc(11.5px * var(--cl-font-scale));
  color: #6a8e6e;
}

/* ════════════════════════════════════════════════════════════════════════════
   MOBILE
   ════════════════════════════════════════════════════════════════════════ */
@media (max-width: 640px) {
  .cl-fab-cluster {
    bottom: 18px;
    right: 18px;
    width: 200px;
    height: 200px;
  }

  .cl-fab {
    width: 64px;
    height: 64px;
  }

  .cl-radial-item {
    width: 52px;
    height: 52px;
  }

  .cl-panel {
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    width: 100%;
    max-width: 100%;
    border-radius: 0;
  }

  .cl-font-slider {
    display: none;
  }
}
</style>
