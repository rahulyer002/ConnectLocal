// Chatbot Store — v4.3
// ─────────────────────────────────────────────────────────────────────────
// v4.3 fixes:
//   • Suggestions are now per-route (welcome state shows prompts that match
//     the page the user is on, not stale prompts from the last conversation)
//   • close() now also resets suggestedPrompts (was only resetting messages)
//
// Set the page suggestions by calling chatbotStore.setSuggestionsForRoute(path)
// from ChatbotButton.vue's onMounted and route-watch.

import { reactive } from 'vue'

// Per-route suggested prompts — what the user sees when the panel first opens
// on a given page. The bot can override these later via the API response.
//
// v5: stale routes (/best-time/now, /best-time/week, /welcoming-spaces) all
// redirect to /best-time so we don't need separate entries. Added /suburb-explorer.
const SUGGESTIONS_BY_ROUTE = {
  '/home': [
    'Find free events near me',
    'Explore my suburb on the map',
    'Is now a good time to go out?',
  ],
  '/discover': [
    'Show only free events',
    'Events this weekend',
    'Plan a journey to one of these',
  ],
  '/journey': [
    'How do I read this route?',
    'Find me a quieter time to travel',
    'Take me back to events',
  ],
  '/best-time': [
    'What do these scores mean?',
    'Find a park with toilets',
    'Show me a welcoming space nearby',
  ],
  '/suburb-explorer': [
    'Show me Carlton',
    'Which suburbs have the best transit?',
    'Take me back to events',
  ],
  '/checkin': [
    'What does this check do?',
    'Is my data private?',
    'Start the check-in',
  ],
  '/results': [
    'What does my score mean?',
    'Find events that might help',
    'Take me to the journey planner',
  ],
}

const DEFAULT_SUGGESTIONS = SUGGESTIONS_BY_ROUTE['/home']

// Look up suggestions for a route path. Tries exact match first, then prefix.
export function suggestionsForRoute(path) {
  if (!path) return DEFAULT_SUGGESTIONS
  if (SUGGESTIONS_BY_ROUTE[path]) return SUGGESTIONS_BY_ROUTE[path]
  // Prefix match — /events/123 → falls through to default; /best-time/foo → /best-time
  for (const key of Object.keys(SUGGESTIONS_BY_ROUTE)) {
    if (path.startsWith(key + '/') || path === key) return SUGGESTIONS_BY_ROUTE[key]
  }
  return DEFAULT_SUGGESTIONS
}

export const chatbotStore = reactive({
  // UI state
  isOpen: false,
  isLoading: false,
  hasUnread: false,

  // Conversation state — always fresh on open
  messages: [],

  // Action state
  pendingAction: null,

  // Suggested prompts — per-route, updated when the panel opens
  suggestedPrompts: [...DEFAULT_SUGGESTIONS],

  // ─── Mutations ──────────────────────────────────────────────────────────
  open() {
    this.isOpen = true
    this.hasUnread = false
  },

  close() {
    this.isOpen = false
    // Full reset — every open is a fresh session
    this.messages = []
    this.pendingAction = null
    this.isLoading = false
    this.suggestedPrompts = [...DEFAULT_SUGGESTIONS]
  },

  toggle() {
    if (this.isOpen) this.close()
    else this.open()
  },

  addUserMessage(content) {
    this.messages.push({
      role: 'user',
      content,
      id: Date.now() + Math.random(),
    })
  },

  addAssistantMessage(content) {
    this.messages.push({
      role: 'assistant',
      content,
      id: Date.now() + Math.random(),
    })
    if (!this.isOpen) this.hasUnread = true
  },

  setPendingAction(action) {
    this.pendingAction = action
  },

  clearPendingAction() {
    this.pendingAction = null
  },

  // Backend can override the suggestions per response — this is called by
  // useChatbot.js when the API returns a `suggested_prompts` field
  setSuggestedPrompts(prompts) {
    if (Array.isArray(prompts) && prompts.length) {
      this.suggestedPrompts = prompts
    }
  },

  // Frontend sets suggestions based on the current Vue route — called from
  // ChatbotButton.vue when the panel opens or the route changes
  setSuggestionsForRoute(path) {
    this.suggestedPrompts = [...suggestionsForRoute(path)]
  },

  setLoading(value) {
    this.isLoading = !!value
  },

  clearConversation() {
    this.messages = []
    this.pendingAction = null
  },
})
