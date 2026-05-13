// useChatbot Composable — v4.2
// ─────────────────────────────────────────────────────────────────────────
// v4.2 fixes:
//   • API base now matches the rest of the app (VITE_ACTIVITIES_API_URL)
//     instead of hardcoded localhost:8000
//   • Error messages now surface the real failure (network/CORS/404)
//     instead of a generic "having trouble connecting"
//
// v4 features retained:
//   • Geocodes suburbs via /api/suburbs/search before navigating
//   • Updates resonanceStore so BestTime/Welcoming pages auto-refetch
//   • Closes the chatbot panel after navigation actions
//   • Param names match what each receiving page already reads

import { useRouter } from 'vue-router'
import { chatbotStore } from '../stores/chatbotStore'
import { resonanceStore } from '../stores/resonanceStore'

// Use the SAME env chain as DiscoverPage/JourneySupportPage etc.
// `VITE_API_BASE_URL` is preferred but if absent we fall through to the
// same `VITE_ACTIVITIES_API_URL` your other API calls already use.
const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_ACTIVITIES_API_URL ||
  'https://connectlocal.duckdns.org'

// Log once on import so devs can confirm which backend the chatbot is hitting
console.info('[chatbot] using API base:', API_BASE)

export function useChatbot() {
  const router = useRouter()

  // ─── Send a message to the backend ──────────────────────────────────────
  async function sendMessage(text) {
    const trimmed = (text || '').trim()
    if (!trimmed || chatbotStore.isLoading) return

    chatbotStore.addUserMessage(trimmed)
    chatbotStore.setLoading(true)
    chatbotStore.clearPendingAction()

    const url = `${API_BASE}/api/chatbot/message`
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: chatbotStore.messages.map((m) => ({
            role: m.role,
            content: m.content,
          })),
          current_route: router.currentRoute.value.path || '/home',
        }),
      })

      if (!response.ok) {
        // Surface the actual server error in console + a useful chat message
        const body = await response.text().catch(() => '')
        console.error('[chatbot] backend returned', response.status, body)
        chatbotStore.addAssistantMessage(
          response.status === 404
            ? "The chatbot service isn't reachable at this address. Check the backend is running and the route is wired up."
            : `The server returned an error (${response.status}). Please try again in a moment.`
        )
        return
      }

      const data = await response.json()

      if (data.reply) chatbotStore.addAssistantMessage(data.reply)
      if (Array.isArray(data.suggested_prompts))
        chatbotStore.setSuggestedPrompts(data.suggested_prompts)

      if (data.proposed_action) {
        if (data.proposed_action.needs_confirmation) {
          chatbotStore.setPendingAction(data.proposed_action)
        } else {
          await executeAction(data.proposed_action)
        }
      }
    } catch (err) {
      // Network-level failure (CORS, DNS, offline). Log loudly + show the
      // user a hint they can act on rather than a generic "try again".
      console.error('[chatbot] network error calling', url, err)
      const hint =
        err?.message?.includes('Failed to fetch') || err?.message?.includes('NetworkError')
          ? "I can't reach the assistant service. If you're running locally, check the backend and CORS settings."
          : "I'm having trouble connecting right now. Please try again in a moment."
      chatbotStore.addAssistantMessage(hint)
    } finally {
      chatbotStore.setLoading(false)
    }
  }

  // ─── Approve / cancel a pending action ──────────────────────────────────
  async function approveAction() {
    const action = chatbotStore.pendingAction
    if (!action) return
    chatbotStore.clearPendingAction()
    await executeAction(action)
  }

  function cancelAction() {
    chatbotStore.clearPendingAction()
    chatbotStore.addAssistantMessage("Okay, I won't do that. Anything else I can help with?")
  }

  // ─── Helper: geocode a suburb name to { lat, lon, name } ────────────────
  async function geocodeSuburb(suburbName) {
    if (!suburbName) return null
    try {
      const r = await fetch(
        `${API_BASE}/api/suburbs/search?q=${encodeURIComponent(suburbName)}&limit=1`
      )
      if (!r.ok) return null
      const data = await r.json()
      const list = data?.suburbs || data || []
      const first = Array.isArray(list) ? list[0] : null
      if (!first) return null
      const lat = first.centroid_lat ?? first.lat
      const lon = first.centroid_lng ?? first.lng ?? first.lon
      if (lat == null || lon == null) return null
      return { lat, lon, name: first.suburb_name ?? first.name ?? suburbName }
    } catch (e) {
      console.warn('[chatbot] geocodeSuburb failed for', suburbName, e)
      return null
    }
  }

  function applyLocationToStore(geo) {
    if (!geo || geo.lat == null || geo.lon == null) return
    resonanceStore.setLocation(geo.lat, geo.lon, geo.name)
  }

  // ─── Action dispatcher ──────────────────────────────────────────────────
  async function executeAction(action) {
    const { name, args = {} } = action
    let closeAfter = true

    switch (name) {
      case 'navigate_to':
        if (args.route) router.push(args.route)
        break

      case 'search_events': {
        const query = {}
        if (args.suburb) query.suburb = args.suburb
        if (args.is_free) query.is_free = 'true'
        if (args.this_week_only) query.this_week = 'true'
        if (args.category) query.category = args.category

        if (args.suburb) {
          const geo = await geocodeSuburb(args.suburb)
          if (geo) {
            query.lat = String(geo.lat)
            query.lon = String(geo.lon)
            applyLocationToStore(geo)
          }
        }
        router.push({ path: '/discover', query })
        break
      }

      case 'plan_journey': {
        const query = { auto: '1' }
        if (args.arrive_by) query.arrive_by = args.arrive_by

        if (args.to_place) {
          query.destination = args.to_place
          query.dest_name = args.to_place
          const geo = await geocodeSuburb(args.to_place)
          if (geo) {
            query.dest_lat = String(geo.lat)
            query.dest_lon = String(geo.lon)
          }
        }

        if (args.from_place) {
          query.from_name = args.from_place
          const fromGeo = await geocodeSuburb(args.from_place)
          if (fromGeo) {
            query.from_lat = String(fromGeo.lat)
            query.from_lon = String(fromGeo.lon)
            applyLocationToStore(fromGeo)
          }
        } else if (resonanceStore.userLat != null) {
          query.from_lat = String(resonanceStore.userLat)
          query.from_lon = String(resonanceStore.userLon)
          query.from_name = resonanceStore.locationLabel || 'My current location'
        }

        router.push({ path: '/journey', query })
        break
      }

      case 'start_checkin':
        router.push('/checkin')
        break

      case 'check_best_time': {
        // v4.3: routes are /best-time/now and /best-time/week (with slashes),
        // not /best-time-now / /best-time-week — see router/index.js
        const path = args.scope === 'week' ? '/best-time/week' : '/best-time/now'
        const query = {}
        if (args.suburb) {
          query.suburb = args.suburb
          const geo = await geocodeSuburb(args.suburb)
          if (geo) {
            query.lat = String(geo.lat)
            query.lon = String(geo.lon)
            applyLocationToStore(geo)
          }
        }
        router.push({ path, query })
        break
      }

      case 'find_welcoming_places': {
        const query = {}
        if (args.suburb) {
          query.suburb = args.suburb
          const geo = await geocodeSuburb(args.suburb)
          if (geo) {
            query.lat = String(geo.lat)
            query.lon = String(geo.lon)
            applyLocationToStore(geo)
          }
        }
        router.push({ path: '/welcoming-spaces', query })
        break
      }

      case 'find_open_spaces': {
        const query = {}
        if (args.suburb) {
          query.suburb = args.suburb
          const geo = await geocodeSuburb(args.suburb)
          if (geo) {
            query.lat = String(geo.lat)
            query.lon = String(geo.lon)
            applyLocationToStore(geo)
          }
        }
        if (args.with_toilets) query.toilets = 'true'
        router.push({ path: '/best-time', query })
        break
      }

      case 'explain_page':
        closeAfter = false
        break

      case 'unknown':
        closeAfter = false
        break

      default:
        console.warn('[chatbot] Unknown action received:', name)
        closeAfter = false
    }

    if (closeAfter) {
      setTimeout(() => chatbotStore.close(), 400)
    }
  }

  return { sendMessage, approveAction, cancelAction }
}
