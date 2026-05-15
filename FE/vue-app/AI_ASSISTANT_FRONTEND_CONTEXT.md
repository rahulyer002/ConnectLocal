# AI Assistant Frontend Context Documentation

## 1. Purpose
This project’s AI assistant is **page-based** and **context-aware** for elderly-friendly outing support.

The assistant does **not** click UI, submit forms, or control navigation directly.  
It only uses current page data to generate:
- suggestions
- explanations
- comparisons
- preparation advice

Primary goal: help users make easier, safer, and lower-stress outing decisions based on what the page is currently showing.

## 2. Global Request Format
Use one unified request payload from frontend to AI backend:

```js
{
  page: string,
  question: string,
  context: object
}
```

Recommended meaning:
- `page`: route-level identifier such as `"discover"` or `"journey"`
- `question`: user’s plain-language request
- `context`: sanitized page snapshot from current frontend state

## 3. Page-by-page Context Design

### 3.1 Home
- Page route: `/home`
- Component file: `src/pages/HomePage.vue`
- Available frontend data:
  - `selectedAgeGroup`
  - `selectedRecord` (computed from `distressData`)
  - `elderlyHighlight`
  - `distressedCount`
  - `sourceText`
  - `isLoading`, `loadError`
- Data source:
  - API: `https://connectlocal.duckdns.org/api/suburbs/psychological-distress`
  - Component state/computed
- Suggested AI question options:
  - “Explain this wellbeing chart for older adults.”
  - “What does this score pattern mean for social support planning?”
- Suggested `pageContext`:
```js
{
  selectedAgeGroup,
  selectedRecord,
  elderlyHighlight,
  distressedCount,
  sourceText,
  loading: isLoading,
  error: loadError
}
```
- Missing/recommended fields:
  - add user-selected suburb context if future home chart becomes location-specific

### 3.2 Discover Events
- Page route: `/discover`
- Component file: `src/pages/DiscoverPage.vue`
- Available frontend data:
  - `locationInput`, `nearbyLabel`
  - `hasLocationConfirmed`, `locationLat`, `locationLon`, `locationQueryMode`
  - `activeFilters` (`free`, `thisWeek`, `closeHome`)
  - `activities` (normalized cards)
  - `totalCount`, `currentPage`, `totalPages`, `visiblePages`
  - `isLoading`, `loadError`
- Data source:
  - API: `${VITE_ACTIVITIES_API_URL}/api/events/search`
  - Geolocation + Nominatim search/reverse
  - Component state/computed
- Suggested AI question options:
  - “Which 2 activities are easiest for a first-time social outing?”
  - “Compare these activities by cost, distance, and social comfort.”
- Suggested `pageContext`:
```js
{
  location: {
    input: locationInput,
    label: nearbyLabel,
    confirmed: hasLocationConfirmed,
    lat: locationLat,
    lon: locationLon,
    queryMode: locationQueryMode
  },
  filters: activeFilters,
  activities,
  pagination: { currentPage, totalPages, totalCount },
  loading: isLoading,
  error: loadError
}
```
- Missing/recommended fields:
  - include selected card id(s) when user taps an item for focused comparison

### 3.3 Event Details
- Page route: `/events/:id`
- Component file: `src/pages/EventDetailsPage.vue`
- Available frontend data:
  - route params/query: `route.params.id`, optional `route.query.lat/lon`
  - `event` raw detail object
  - computed display fields: `priceText`, `dateTimeText`, `venueText`, `distanceText`, `restrictionsText`
  - `isLoading`, `loadError`
- Data source:
  - API: `${VITE_ACTIVITIES_API_URL}/api/events/:id`
  - Route param/query
- Suggested AI question options:
  - “How suitable is this event for someone anxious about crowds?”
  - “What should I prepare before going to this event?”
- Suggested `pageContext`:
```js
{
  eventId: route.params.id,
  event,
  display: { priceText, dateTimeText, venueText, distanceText, restrictionsText },
  loading: isLoading,
  error: loadError
}
```
- Missing/recommended fields:
  - add `event.latitude/event.longitude` if backend can provide stable venue coordinates

### 3.4 Journey Support
- Page route: `/journey`
- Component file: `src/pages/JourneySupportPage.vue`
- Available frontend data:
  - from/to input and coordinates:
    - `fromLocation`, `fromLat`, `fromLon`, `fromLocationConfirmed`
    - `toLocation`, `toLat`, `toLon`
  - route prefill from query:
    - `route.query.destination`
  - API route result (`planData`):
    - summary: `mode`, `provider`, `route_index`, `summary`
    - totals: `total_duration_label`, `total_distance_label`, `total_walk_label`, `departure_time`, `arrival_time`, `leave_home_by`
    - `warnings`, `legs_summary`, `steps`, `waypoints`
  - derived:
    - `displayLegs`, `displaySteps`, `displayWarnings`
    - `firstTransitVehicle`, `firstTransitDeparture`
  - UI states: `isPlanning`, `mapError`, `planError`
- Data source:
  - API: `${VITE_ACTIVITIES_API_URL}/api/journey/google/plan`
  - Geolocation + Nominatim
  - Route query (`destination`)
- Suggested AI question options:
  - “Explain this route in simple elderly-friendly language.”
  - “What are the stressful parts of this journey and alternatives?”
- Suggested `pageContext`:
```js
{
  from: { text: fromLocation, lat: fromLat, lon: fromLon, confirmed: fromLocationConfirmed },
  to: { text: toLocation, lat: toLat, lon: toLon },
  routeResult: planData,
  routeSummary: displayLegs,
  stepByStep: displaySteps,
  warnings: displayWarnings,
  transitQuickInfo: {
    vehicle: firstTransitVehicle,
    departure: firstTransitDeparture
  },
  errors: { mapError, planError },
  loading: isPlanning
}
```
- Missing/recommended fields:
  - selected route index if multi-route UI is added later
  - explicit accessibility flags (stairs, slope, transfer difficulty) if backend exposes them

### 3.5 Check-in Landing
- Page route: `/checkin`
- Component file: `src/pages/CheckinPage.vue`
- Available frontend data:
  - mostly static page content
- Data source:
  - component constants
- Suggested AI question options:
  - “What will this check-in help me understand?”
- Suggested `pageContext`:
```js
{
  stage: "landing"
}
```
- Missing/recommended fields:
  - no major additions required

### 3.6 Check-in Form
- Page route: `/checkin/form`
- Component file: `src/pages/CheckinFormPage.vue`
- Available frontend data:
  - `questions`
  - `currentQuestionIndex`, `currentQuestion`, `currentQuestionNumber`
  - `answers`
  - `progressPercent`
  - `showValidation`
- Data source:
  - component state
  - writes final output to `wellbeingStore`
- Suggested AI question options:
  - “Help me interpret this question in plain words.”
  - “I feel unsure, how should I answer honestly?”
- Suggested `pageContext`:
```js
{
  currentQuestionIndex,
  currentQuestion,
  currentQuestionNumber,
  progressPercent,
  answeredCount: answers.filter(v => v !== null).length,
  totalQuestions: questions.length,
  showValidation
}
```
- Missing/recommended fields:
  - do not send full answer history by default unless user asks for deep interpretation

### 3.7 Check-in Results
- Page route: `/results`
- Component file: `src/pages/ResultsPage.vue`
- Available frontend data:
  - `wellbeingStore.hasResult`
  - `wellbeingStore.totalScore`
  - `wellbeingStore.resultBand`
  - `wellbeingStore.resultExplanation`
  - `wellbeingStore.dimensionScores`
  - computed: `resultBandClass`, `nextStepText`
- Data source:
  - `wellbeingStore`
- Suggested AI question options:
  - “What does my result mean in daily life?”
  - “Give me a gentle 7-day social reconnection plan.”
- Suggested `pageContext`:
```js
{
  hasResult: wellbeingStore.hasResult,
  totalScore: wellbeingStore.totalScore,
  resultBand: wellbeingStore.resultBand,
  resultExplanation: wellbeingStore.resultExplanation,
  dimensionScores: wellbeingStore.dimensionScores,
  nextStepText
}
```
- Missing/recommended fields:
  - date/timestamp of latest completed check-in

### 3.8 Best Time (Overview)
- Page route: `/best-time`
- Component file: `src/pages/BestTimePage.vue`
- Available frontend data:
  - shared store location: `resonanceStore.userLat/userLon/locationLabel/locationReady`
  - score block: `scoreResult`, `breakdownItems`, `gradeColor`, `scoreArc`
  - safety block: `safetyConditions`
  - best historical windows: `bestTimesResult.best_times`
  - loading flags: `loadingScore`
- Data source:
  - `resonanceStore`
  - API via `useResonanceApi` (`/api/resonance/score`, `/api/safety/conditions`, `/api/resonance/besttimes`)
- Suggested AI question options:
  - “Is now a good time for a low-stress outing?”
  - “Explain what drives this score and what to watch out for.”
- Suggested `pageContext`:
```js
{
  location: {
    ready: resonanceStore.locationReady,
    lat: resonanceStore.userLat,
    lon: resonanceStore.userLon,
    label: resonanceStore.locationLabel
  },
  scoreResult: resonanceStore.scoreResult,
  safetyConditions: resonanceStore.safetyConditions,
  bestTimes: resonanceStore.bestTimesResult?.best_times ?? [],
  loading: resonanceStore.loadingScore
}
```
- Missing/recommended fields:
  - include confidence metadata from backend if available

### 3.9 Best Time Now
- Page route: `/best-time/now`
- Component file: `src/pages/BestTimeNowPage.vue`
- Available frontend data:
  - `goNowResult.recommendations`
  - `safetyConditions`
  - `nearbyToilets`, `nearbyStops`
  - derived: `nearestToilet`, `nearbyStops`
  - loading flag: `loadingGoNow`
- Data source:
  - `resonanceStore`
  - API via `useResonanceApi` (`/api/resonance/gonow`, `/api/safety/conditions`, `/api/greenspace/toilets`, `/api/journey/stops/nearby`)
- Suggested AI question options:
  - “Which nearby place is best for me right now and why?”
  - “Compare top 2 spots by comfort and access.”
- Suggested `pageContext`:
```js
{
  location: {
    ready: resonanceStore.locationReady,
    lat: resonanceStore.userLat,
    lon: resonanceStore.userLon,
    label: resonanceStore.locationLabel
  },
  recommendations: resonanceStore.goNowResult?.recommendations ?? [],
  safetyConditions: resonanceStore.safetyConditions,
  nearbyToilets: resonanceStore.nearbyToilets ?? [],
  nearbyStops: resonanceStore.nearbyStops ?? [],
  loading: resonanceStore.loadingGoNow
}
```
- Missing/recommended fields:
  - estimated walking time to each recommendation

### 3.10 Best Time Week
- Page route: `/best-time/week`
- Component file: `src/pages/BestTimeWeekPage.vue`
- Available frontend data:
  - `forecastResult.forecast_days`
  - hourly forecast matrix from `forecastResult.forecast`
  - `selectedCell`
  - derived: `quietestDay`, `maxCount`
  - `greenSpaces`
  - loading flags: `loadingForecast`, `loadingSpaces`
- Data source:
  - `resonanceStore`
  - API via `useResonanceApi` (`/api/resonance/forecast`, `/api/greenspace/nearby`)
- Suggested AI question options:
  - “Which day/hour is quietest for me this week?”
  - “Plan two possible outing windows with fallback times.”
- Suggested `pageContext`:
```js
{
  location: {
    ready: resonanceStore.locationReady,
    lat: resonanceStore.userLat,
    lon: resonanceStore.userLon,
    label: resonanceStore.locationLabel
  },
  forecastDays: resonanceStore.forecastResult?.forecast_days ?? [],
  forecast: resonanceStore.forecastResult?.forecast ?? {},
  selectedCell,
  quietestDay,
  greenSpaces: resonanceStore.greenSpaces ?? [],
  loading: {
    forecast: resonanceStore.loadingForecast,
    spaces: resonanceStore.loadingSpaces
  }
}
```
- Missing/recommended fields:
  - weather risk labels per hour if backend adds them

### 3.11 Welcoming Spaces
- Page route: `/welcoming-spaces`
- Component file: `src/pages/WelcomingSpacesPage.vue`
- Available frontend data:
  - `searchRadius`
  - `allLandmarks`
  - derived:
    - `welcomingSpaces`
    - `communityLandmarks`
  - `loading`
- Data source:
  - `resonanceStore` location
  - API via `useResonanceApi` (`/api/landmarks/nearby`)
- Suggested AI question options:
  - “Which welcoming space is best for first visit?”
  - “Compare library vs community centre based on comfort.”
- Suggested `pageContext`:
```js
{
  location: {
    ready: resonanceStore.locationReady,
    lat: resonanceStore.userLat,
    lon: resonanceStore.userLon,
    label: resonanceStore.locationLabel
  },
  searchRadius,
  allLandmarks,
  welcomingSpaces,
  communityLandmarks,
  loading
}
```
- Missing/recommended fields:
  - opening hours and accessibility details per landmark

## 4. Recommended Reusable Component
Suggested component: `src/components/AIOutingAssistant.vue`

Recommended props:
```js
props: {
  page: { type: String, required: true },
  pageContext: { type: Object, required: true },
  defaultQuestions: { type: Array, default: () => [] }
}
```

Recommended emitted events:
- `ask` with `{ question }`
- `error` with error object/message

Recommended internal state:
- `inputQuestion`
- `selectedPrompt`
- `loading`
- `answer`
- `error`

Component behavior:
- shows quick question chips per page
- sends one structured request to AI backend
- renders markdown/text response
- keeps history local to current page instance (optional)

## 5. Recommended API Client Function
Create `src/composables/useAiAssistantApi.js`:

```js
const AI_BASE_URL = import.meta.env.VITE_AI_API_URL

export async function askAI(page, question, context) {
  const res = await fetch(`${AI_BASE_URL}/api/assistant/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ page, question, context })
  })
  if (!res.ok) throw new Error(`AI API ${res.status}`)
  return await res.json()
}
```

Recommended response shape:
```js
{
  answer: string,
  suggestions?: string[],
  cautions?: string[],
  references?: string[]
}
```

## 6. Implementation Notes
- Use explicit loading states to avoid duplicate asks while a request is pending.
- Always handle network and parsing errors with user-safe fallback text.
- Validate response type before rendering (`answer` must be string).
- Do not send unnecessary personal data:
  - avoid exact identity info
  - avoid full free-text history unless needed
  - round coordinates if exact precision is not required
- For sensitive pages (check-in/results), send summary context by default and only include detailed answers when user explicitly asks for deeper interpretation.
- Keep context page-scoped:
  - build `pageContext` from current page state only
  - avoid mixing data from unrelated pages unless intentionally linked by route query/store.
