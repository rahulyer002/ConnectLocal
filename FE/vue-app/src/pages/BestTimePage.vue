<template>
  <MainLayout>
    <div class="best-time-page">
      <div class="noise" aria-hidden="true"></div>
      <div class="orb orb-1" aria-hidden="true"></div>
      <div class="orb orb-2" aria-hidden="true"></div>

      <section class="hero">
        <div class="hero-bg-word" aria-hidden="true">TIMING</div>
        <div class="hero-inner">
          <p class="hero-eyebrow"><span class="eyebrow-line" aria-hidden="true"></span>Personalised timing engine</p>
          <h1 class="hero-headline">When is the<br><em>best time</em> for you?</h1>
          <p class="hero-sub" :style="{ fontSize: scaledPx(18) }">
            Four quick steps, answered with live data. Conditions right now, when to head out this week, where to go, and welcoming spaces to drop in to.
          </p>
        </div>
      </section>

      <!-- Sticky zone: location bar (always) + step nav (when location ready) stay
           pinned to the top of the viewport as the user scrolls. -->
      <div class="bt-sticky-zone">
        <BestTimeLocationBar />

        <nav v-if="store.locationReady" class="bt-step-nav" role="navigation" aria-label="Page steps">
          <div class="bt-step-nav-inner">
            <button v-for="(s, i) in steps" :key="s.id" type="button" class="bt-step-pill" :class="{ active: activeSection === s.id }" @click="scrollToSection(s.id)">
              <span class="bt-step-num">{{ i + 1 }}</span>
              <span class="bt-step-label">{{ s.label }}</span>
            </button>
          </div>
        </nav>
      </div>

      <section v-if="!store.locationReady" class="empty-band">
        <div class="empty-card">
          <svg viewBox="0 0 24 24" width="56" height="56" fill="none" stroke="#0a9b8a" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>
          <h3 :style="{ fontSize: scaledPx(24) }">Tell us where you are</h3>
          <p :style="{ fontSize: scaledPx(16) }">Type a Melbourne suburb or postcode, or tap "Locate me".</p>
          <div class="empty-tip" :style="{ fontSize: scaledPx(13) }"><strong>Heads up:</strong> Historical foot-traffic data covers the City of Melbourne CBD and inner suburbs. Live score, best spots, and welcoming spaces work for anywhere in greater Melbourne.</div>
        </div>
      </section>

      <template v-else>
        <!-- STEP 1 · RIGHT NOW -->
        <section id="right-now" class="bt-section section-light">
          <header class="bt-section-head">
            <p class="section-label"><span class="step-tag">Step 1</span> Right now</p>
            <h2 class="section-heading" :style="{ fontSize: scaledPx(40) }">How does today<br><em>feel out there?</em></h2>
            <p class="section-sub" :style="{ fontSize: scaledPx(16) }">A live read on weather, crowds, and comfort around {{ store.locationLabel }}, updated every 15 minutes.</p>
          </header>

          <div class="dashboard-band">
            <div v-if="store.loadingScore && !store.scoreResult" class="loading-row"><div class="spinner" aria-hidden="true"></div><p :style="{ fontSize: scaledPx(15) }">Checking live conditions…</p></div>
            <div v-else-if="scoreError" class="data-error"><p :style="{ fontSize: scaledPx(15) }">We couldn't load live conditions. Check your connection or try a different location.</p></div>
            <div v-else-if="store.scoreResult && store.scoreResult.has_data === false" class="no-sensor-band inline-no-sensor">
              <div class="no-sensor-card">
                <svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="#b88a00" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                <h3 :style="{ fontSize: scaledPx(20) }">Live score not available here</h3>
                <p :style="{ fontSize: scaledPx(15) }">The resonance score relies on the City of Melbourne pedestrian sensor network, which covers the CBD and inner suburbs. We don't have live readings for <strong>{{ store.locationLabel }}</strong> yet.</p>
                <div class="no-sensor-actions">
                  <button type="button" class="no-sensor-btn primary" @click="useCbdLocation">Try Melbourne CBD instead</button>
                  <button type="button" class="no-sensor-btn outline" @click="scrollToSection('where-to-go')">Skip to where to go ↓</button>
                </div>
              </div>
            </div>
            <div v-else-if="store.scoreResult && store.scoreResult.resonance_score != null" class="dashboard-inner">
              <div class="dash-score">
                <div class="ring-wrap">
                  <svg class="ring" viewBox="0 0 180 180" aria-hidden="true">
                    <circle class="ring-track" cx="90" cy="90" r="76"/>
                    <circle class="ring-fill" cx="90" cy="90" r="76" :stroke="gradeColor" :stroke-dasharray="`${scoreArc} ${478 - scoreArc}`" stroke-dashoffset="119"/>
                  </svg>
                  <div class="ring-text">
                    <span class="ring-num" :style="{ fontSize: scaledPx(56) }">{{ Math.round(store.scoreResult.resonance_score) }}</span>
                    <span class="ring-out" :style="{ fontSize: scaledPx(13) }">/ 100</span>
                  </div>
                </div>
                <span class="grade-pill" :style="{ background: gradeColor, fontSize: scaledPx(13) }">{{ store.scoreResult.grade }} conditions</span>
              </div>
              <div class="dash-breakdown">
                <p class="dash-label">What makes up your score</p>
                <div v-for="item in breakdownItems" :key="item.label" class="bar-row">
                  <span class="bar-label" :style="{ fontSize: scaledPx(14) }">{{ item.label }}</span>
                  <div class="bar-track"><div class="bar-fill" :style="{ width: `${(item.value / item.max) * 100}%`, background: item.color }"></div></div>
                  <span class="bar-pts" :style="{ fontSize: scaledPx(13) }">{{ formatPts(item.value) }}<span class="bar-max">/{{ item.max }}</span></span>
                </div>
              </div>
              <div v-if="store.scoreResult.weather" class="dash-weather">
                <p class="dash-label">Right now</p>
                <div class="weather-grid">
                  <div class="weather-tile"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></svg><span class="w-num" :style="{ fontSize: scaledPx(20) }">{{ store.scoreResult.weather.temperature_c }}°</span><span class="w-label" :style="{ fontSize: scaledPx(10) }">Temp</span></div>
                  <div class="weather-tile"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9.59 4.59A2 2 0 1 1 11 8H2m10.59 11.41A2 2 0 1 0 14 16H2m15.73-8.27A2.5 2.5 0 1 1 19.5 12H2"/></svg><span class="w-num" :style="{ fontSize: scaledPx(20) }">{{ store.scoreResult.weather.wind_speed_kmh }}</span><span class="w-label" :style="{ fontSize: scaledPx(10) }">km/h wind</span></div>
                  <div class="weather-tile"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg><span class="w-num" :style="{ fontSize: scaledPx(20) }">{{ store.scoreResult.weather.humidity_pct }}%</span><span class="w-label" :style="{ fontSize: scaledPx(10) }">Humidity</span></div>
                  <div class="weather-tile"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/></svg><span class="w-num" :style="{ fontSize: scaledPx(20) }">{{ store.scoreResult.weather.pm25_ug_m3 }}</span><span class="w-label" :style="{ fontSize: scaledPx(10) }">PM2.5</span></div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="store.safetyConditions?.has_data !== false && store.safetyConditions?.conditions" class="safety-strip" :class="`verdict-${(store.safetyConditions.conditions.safety_verdict || 'unknown').toLowerCase()}`" role="status">
            <div class="safety-inner">
              <span class="safety-dot" aria-hidden="true"></span>
              <p :style="{ fontSize: scaledPx(15) }"><strong>{{ store.safetyConditions.conditions.safety_verdict }} conditions</strong><span v-if="store.safetyConditions.advice"> - {{ store.safetyConditions.advice }}</span></p>
            </div>
          </div>
        </section>

        <!-- STEP 2 · WHEN YOU GO -->
        <section id="when-you-go" class="bt-section section-cream">
          <header class="bt-section-head">
            <p class="section-label"><span class="step-tag">Step 2</span> When you go<span class="data-source-pill">City of Melbourne sensor data</span></p>
            <h2 class="section-heading" :style="{ fontSize: scaledPx(40) }">
              <template v-if="hasSensorData">Quiet windows<br><em>this week.</em></template>
              <template v-else>Historical patterns<br><em>aren't available here.</em></template>
            </h2>
            <p class="section-sub" :style="{ fontSize: scaledPx(16) }">
              <template v-if="hasSensorData">Built from 2 years of City of Melbourne pedestrian sensor data. Tap any day pill to see its hourly pattern.</template>
              <template v-else>{{ noSensorMessage }}</template>
            </p>
          </header>

          <div v-if="(store.loadingForecast || !forecastFetched) && !hasSensorData && !showNoSensorState" class="loading-row"><div class="spinner" aria-hidden="true"></div><p :style="{ fontSize: scaledPx(15) }">Loading historical patterns…</p></div>

          <div v-else-if="showNoSensorState" class="no-sensor-band">
            <div class="no-sensor-card">
              <svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="#b88a00" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              <h3 :style="{ fontSize: scaledPx(20) }">Outside sensor coverage</h3>
              <p :style="{ fontSize: scaledPx(15) }">The pedestrian counting system covers the CBD and inner suburbs. We don't have foot-traffic patterns for <strong>{{ store.locationLabel }}</strong> yet.</p>
              <div class="no-sensor-actions">
                <button type="button" class="no-sensor-btn primary" @click="useCbdLocation">Try Melbourne CBD instead</button>
                <button type="button" class="no-sensor-btn outline" @click="scrollToSection('where-to-go')">Skip to where to go ↓</button>
              </div>
            </div>
          </div>

          <div v-else-if="hasSensorData" class="week-band">
            <div v-if="topQuietWindow" class="best-window-banner">
              <div class="bw-star">★</div>
              <div class="bw-content">
                <p class="bw-eyebrow">Best window this week</p>
                <p class="bw-line"><strong>{{ topQuietWindow.day_name }} at {{ topQuietWindow.hour_label }}</strong> - your quietest moment, around {{ Math.round(topQuietWindow.avg_count) }} people/hr.</p>
              </div>
            </div>

            <div class="week-split">
              <div class="week-chart-card">
                <p class="week-col-label">Hourly crowd by day</p>
                <CrowdDayChart :forecast="store.forecastResult?.forecast || {}" />
                <p class="chart-foot" :style="{ fontSize: scaledPx(12) }">Click a day pill to switch. Tap any bar to pin it. Green = quieter, amber = moderate, red = busier.</p>
              </div>
              <div class="week-summary-card">
                <p class="week-col-label">Top quiet windows</p>
                <p class="summary-hint" :style="{ fontSize: scaledPx(13) }">The single best moments to visit, ranked by historical foot traffic.</p>
                <ol class="quiet-list">
                  <li v-for="(t, i) in (store.bestTimesResult?.best_times || [])" :key="`${t.day_name}-${t.hour_label}-${i}`" class="quiet-row" :class="{ 'quiet-row-best': i === 0 }">
                    <span class="quiet-rank">{{ i + 1 }}<span v-if="i === 0" class="quiet-rank-tag">Best</span></span>
                    <div class="quiet-info">
                      <span class="quiet-day" :style="{ fontSize: scaledPx(16) }">{{ t.day_name }}</span>
                      <span class="quiet-hour" :style="{ fontSize: scaledPx(13) }">{{ t.hour_label }}</span>
                      <div class="quiet-meta">
                        <span class="crowd-pip" :class="`crowd-${t.crowd_level.toLowerCase()}`">{{ t.crowd_level }}</span>
                        <span class="quiet-count">~{{ Math.round(t.avg_count) }} people/hr</span>
                      </div>
                    </div>
                  </li>
                </ol>
              </div>
            </div>
          </div>
        </section>

        <!-- STEP 3 · WHERE TO GO -->
        <section id="where-to-go" class="bt-section section-mint">
          <header class="bt-section-head">
            <p class="section-label"><span class="step-tag">Step 3</span> Where to go</p>
            <h2 class="section-heading" :style="{ fontSize: scaledPx(40) }">Top picks within<br><em>walking distance.</em></h2>
            <p class="section-sub" :style="{ fontSize: scaledPx(16) }">Live-scored top picks first, then a wider list of comfortable parks you can sort and filter.</p>
          </header>

          <div v-if="store.loadingGoNow && !goNowSpots.length" class="loading-row"><div class="spinner" aria-hidden="true"></div><p :style="{ fontSize: scaledPx(15) }">Finding best spots near you…</p></div>
          <div v-else-if="!goNowSpots.length" class="empty-inline"><p :style="{ fontSize: scaledPx(15) }">No matching spots within walking distance. Try a different location.</p></div>

          <div v-else class="spots-wrap">
            <article class="featured-card" :data-grade="(goNowSpots[0].grade || '').toLowerCase()">
              <div class="featured-head">
                <div class="featured-title-block">
                  <p class="rank-eyebrow"><span class="rank-circle">1</span>Top pick right now</p>
                  <h3 class="featured-name" :style="{ fontSize: scaledPx(38) }">{{ goNowSpots[0].space_name }}</h3>
                  <p class="featured-meta">
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>
                    {{ goNowSpots[0].distance_km?.toFixed(1) }} km away
                    <span class="grade-chip" :class="`grade-${(goNowSpots[0].grade || '').toLowerCase()}`">{{ goNowSpots[0].grade }}</span>
                  </p>
                </div>
                <div class="featured-score-ring">
                  <svg class="ring" viewBox="0 0 130 130" aria-hidden="true">
                    <circle class="ring-track" cx="65" cy="65" r="56"/>
                    <circle class="ring-fill" cx="65" cy="65" r="56" :stroke="recRingColor(goNowSpots[0].resonance_score)" :stroke-dasharray="`${(Math.max(0,Math.min(100, goNowSpots[0].resonance_score))/100) * 352} 352`" stroke-dashoffset="88"/>
                  </svg>
                  <div class="ring-text">
                    <span class="score-num" :style="{ fontSize: scaledPx(44) }">{{ Math.round(goNowSpots[0].resonance_score) }}</span>
                    <span class="score-out">/ 100</span>
                  </div>
                </div>
              </div>
              <p v-if="goNowSpots[0].why_recommended" class="featured-why" :style="{ fontSize: scaledPx(16) }">{{ goNowSpots[0].why_recommended }}</p>
              <div class="featured-tags">
                <span class="info-tag" :class="`crowd-${(goNowSpots[0].crowd_level || 'unknown').toLowerCase()}`">{{ goNowSpots[0].crowd_level }}<span v-if="goNowSpots[0].is_quiet_now"> · Quiet now</span></span>
                <span v-if="goNowSpots[0].has_toilet_nearby" class="info-tag tag-toilet">✓ Toilet nearby</span>
                <span v-else class="info-tag tag-no-toilet">⚠ No toilet within 200m</span>
              </div>
              <div class="featured-actions">
                <button class="get-there-btn primary" @click="planJourney(goNowSpots[0])">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
                  Plan my journey
                </button>
                <a :href="`https://www.google.com/maps/dir/?api=1&amp;origin=${store.userLat},${store.userLon}&amp;destination=${goNowSpots[0].lat},${goNowSpots[0].lon}&amp;travelmode=walking`" target="_blank" rel="noopener" class="get-there-btn outline">
                  Open in Maps
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
                </a>
              </div>
            </article>

            <div v-if="goNowSpots.length > 1" class="runners-band">
              <h3 class="runners-heading" :style="{ fontSize: scaledPx(24) }">Other great options</h3>
              <div class="runners-grid">
                <article v-for="(spot, i) in goNowSpots.slice(1, 3)" :key="spot.space_id || i" class="runner-card">
                  <div class="runner-head"><span class="runner-rank">{{ i + 2 }}</span><span class="grade-chip" :class="`grade-${(spot.grade || '').toLowerCase()}`">{{ spot.grade }}</span></div>
                  <h4 class="runner-name" :style="{ fontSize: scaledPx(22) }">{{ spot.space_name }}</h4>
                  <p class="runner-meta">{{ spot.distance_km?.toFixed(1) }} km away</p>
                  <div class="runner-score-strip">
                    <span class="runner-score-num">{{ Math.round(spot.resonance_score) }}</span>
                    <span class="runner-score-bar"><span class="bar-inner" :style="{ width: `${Math.min(100, spot.resonance_score)}%` }"></span></span>
                  </div>
                  <p v-if="spot.why_recommended" class="runner-why" :style="{ fontSize: scaledPx(13) }">{{ spot.why_recommended }}</p>
                  <div class="runner-tags">
                    <span class="info-tag-sm" :class="`crowd-${(spot.crowd_level || 'unknown').toLowerCase()}`">{{ spot.crowd_level }}</span>
                    <span v-if="spot.has_toilet_nearby" class="info-tag-sm tag-toilet">Toilet nearby</span>
                  </div>
                  <button class="get-there-btn outline small" @click="planJourney(spot)">
                    Plan my journey
                    <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
                  </button>
                </article>
              </div>
            </div>
          </div>

        </section>

        <!-- ═══ GREEN SPACES BAND (inline, full implementation from old code) ═══ -->
        <section v-if="store.locationReady" id="green-spaces" class="spaces-band">
          <div class="spaces-inner">
            <!-- Full-width 3-card stats strip -->
            <div v-if="!store.loadingSpaces && totalSpacesCount > 0" class="stats-strip">
              <div class="stat-card-big">
                <div class="stat-icon-big mint">
                  <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M2 22c1.25-1.25 2.5-2.5 3.5-4C7 16 8 13.5 8 11c0-5.5 4.5-9 9-9 0 4.5-1 8-3.5 10.5S8.5 16 6 18c-1 1-2.5 2.5-4 4z"/>
                  </svg>
                </div>
                <span class="stat-num-big" :style="{ fontSize: scaledPx(56) }">{{ totalSpacesCount }}</span>
                <span class="stat-label-big">Parks within 2km</span>
              </div>
              <div class="stat-card-big">
                <div class="stat-icon-big purple">
                  <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <rect x="9" y="2" width="6" height="20" rx="1"/>
                    <rect x="2" y="9" width="20" height="6" rx="1"/>
                  </svg>
                </div>
                <span class="stat-num-big" :style="{ fontSize: scaledPx(56) }">{{ toiletParksCount }}</span>
                <span class="stat-label-big">With toilets nearby</span>
              </div>
              <div class="stat-card-big">
                <div class="stat-icon-big yellow">
                  <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                  </svg>
                </div>
                <span class="stat-num-big" :style="{ fontSize: scaledPx(56) }">{{ topComfortScore }}</span>
                <span class="stat-label-big">Top comfort score</span>
              </div>
            </div>

            <div class="spaces-band-header">
              <div class="title-with-animation">
                <div class="spaces-band-title">
                  <p class="section-label">Comfortable parks near you</p>
                  <h2 class="section-heading" :style="{ fontSize: scaledPx(40) }">
                    Green spaces<br><em>ranked &amp; filtered.</em>
                  </h2>
                  <p class="section-sub" :style="{ fontSize: scaledPx(15) }">
                    Comfort score combines walkability, shade, and toilet access. Walkability scores are normalised against the highest in your search area.
                  </p>
                </div>

                <!-- ─── Animated park scene ─── -->
                <div class="park-animation" aria-hidden="true">
                  <svg viewBox="0 0 320 240" class="park-svg">
                    <defs>
                      <linearGradient id="psky" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stop-color="#e0f5e8"/>
                        <stop offset="100%" stop-color="#f0faf0"/>
                      </linearGradient>
                      <linearGradient id="pgrass" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stop-color="#7bbf80"/>
                        <stop offset="100%" stop-color="#4a9a5a"/>
                      </linearGradient>
                      <radialGradient id="psun" cx="50%" cy="50%" r="50%">
                        <stop offset="0%" stop-color="#ffd56b"/>
                        <stop offset="100%" stop-color="#ffb83a"/>
                      </radialGradient>
                    </defs>
                    <rect width="320" height="180" fill="url(#psky)"/>
                    <g class="park-sun" style="transform-origin: 260px 50px">
                      <g class="sun-rays">
                        <line x1="260" y1="20" x2="260" y2="14" stroke="#ffcc44" stroke-width="2" stroke-linecap="round"/>
                        <line x1="260" y1="80" x2="260" y2="86" stroke="#ffcc44" stroke-width="2" stroke-linecap="round"/>
                        <line x1="230" y1="50" x2="224" y2="50" stroke="#ffcc44" stroke-width="2" stroke-linecap="round"/>
                        <line x1="290" y1="50" x2="296" y2="50" stroke="#ffcc44" stroke-width="2" stroke-linecap="round"/>
                        <line x1="239" y1="29" x2="234" y2="24" stroke="#ffcc44" stroke-width="2" stroke-linecap="round"/>
                        <line x1="281" y1="71" x2="286" y2="76" stroke="#ffcc44" stroke-width="2" stroke-linecap="round"/>
                        <line x1="281" y1="29" x2="286" y2="24" stroke="#ffcc44" stroke-width="2" stroke-linecap="round"/>
                        <line x1="239" y1="71" x2="234" y2="76" stroke="#ffcc44" stroke-width="2" stroke-linecap="round"/>
                      </g>
                      <circle cx="260" cy="50" r="16" fill="url(#psun)"/>
                    </g>
                    <g class="park-cloud c1" fill="white" opacity="0.92">
                      <ellipse cx="60" cy="40" rx="22" ry="8"/>
                      <ellipse cx="48" cy="36" rx="11" ry="8"/>
                      <ellipse cx="72" cy="35" rx="13" ry="8"/>
                    </g>
                    <g class="park-cloud c2" fill="white" opacity="0.85">
                      <ellipse cx="160" cy="60" rx="16" ry="6"/>
                      <ellipse cx="152" cy="56" rx="9" ry="6"/>
                      <ellipse cx="168" cy="56" rx="10" ry="6"/>
                    </g>
                    <g class="park-bird b1" fill="none" stroke="#2d5a3d" stroke-width="1.5" stroke-linecap="round"><path d="M0 0 q3-4 6 0 q3-4 6 0"/></g>
                    <g class="park-bird b2" fill="none" stroke="#2d5a3d" stroke-width="1.3" stroke-linecap="round"><path d="M0 0 q2.5-3 5 0 q2.5-3 5 0"/></g>
                    <path d="M0 160 Q80 130 160 152 T320 145 L320 200 L0 200Z" fill="#a8d8a8" opacity="0.7"/>
                    <path d="M0 178 L320 178 L320 240 L0 240 Z" fill="url(#pgrass)"/>
                    <path d="M-20 240 Q120 218 160 212 Q200 218 340 240" stroke="#d4b87a" stroke-width="22" fill="none" stroke-linecap="round" opacity="0.85"/>
                    <path d="M-20 240 Q120 218 160 212 Q200 218 340 240" stroke="#e4cfa0" stroke-width="14" fill="none" stroke-linecap="round"/>
                    <g class="park-tree t-left" style="transform-origin: 50px 195px">
                      <rect x="47" y="170" width="6" height="32" fill="#5a3a1a"/>
                      <circle cx="50" cy="166" r="22" fill="#3e8a4a"/>
                      <circle cx="38" cy="160" r="14" fill="#5cb471"/>
                      <circle cx="62" cy="162" r="14" fill="#4fae6b"/>
                      <circle cx="50" cy="148" r="12" fill="#6cc481"/>
                    </g>
                    <g class="park-tree t-right" style="transform-origin: 280px 200px">
                      <rect x="278" y="178" width="5" height="26" fill="#5a3a1a"/>
                      <circle cx="280" cy="174" r="17" fill="#3e8a4a"/>
                      <circle cx="271" cy="170" r="11" fill="#5cb471"/>
                      <circle cx="289" cy="172" r="11" fill="#4fae6b"/>
                    </g>
                    <g transform="translate(110 200)">
                      <rect x="-22" y="-8" width="44" height="3" fill="#6b4226" rx="1"/>
                      <rect x="-22" y="-3" width="44" height="3" fill="#6b4226" rx="1"/>
                      <rect x="-20" y="0" width="3" height="10" fill="#6b4226"/>
                      <rect x="17" y="0" width="3" height="10" fill="#6b4226"/>
                    </g>
                    <g class="park-person" transform="translate(190 215)">
                      <ellipse cx="0" cy="6" rx="8" ry="1.5" fill="#000" opacity="0.15"/>
                      <g class="person-body">
                        <rect class="leg-back" x="-2" y="-4" width="3" height="9" rx="1.5" fill="#234"/>
                        <rect class="leg-front" x="-1" y="-4" width="3" height="9" rx="1.5" fill="#345"/>
                        <path d="M-6-15 Q-7-7 -5-3 L5-3 Q7-7 6-15 Q3-17 0-17 Q-3-17 -6-15Z" fill="#0a9b8a"/>
                        <g class="arm-wave" style="transform-origin: 5px -13px">
                          <rect x="4" y="-13" width="2.5" height="9" rx="1.2" fill="#0a9b8a"/>
                          <circle cx="5" cy="-3" r="1.5" fill="#f0c8a0"/>
                        </g>
                        <rect x="-7" y="-13" width="2.5" height="9" rx="1.2" fill="#0a9b8a"/>
                        <circle cx="-5.5" cy="-3" r="1.5" fill="#f0c8a0"/>
                        <rect x="-1.5" y="-19" width="3" height="3" fill="#f0c8a0"/>
                        <circle cx="0" cy="-22" r="5.5" fill="#f0c8a0"/>
                        <path d="M-5.5-22 Q-5-29 0-29 Q5-29 5.5-22 Q3-26 0-25 Q-3-26 -5.5-22Z" fill="#3a2010"/>
                      </g>
                    </g>
                    <g class="park-butterfly">
                      <g class="bf-wings">
                        <ellipse cx="-2" cy="-1" rx="2.5" ry="3.5" fill="#c44a8a" opacity="0.85"/>
                        <ellipse cx="2" cy="-1" rx="2.5" ry="3.5" fill="#e89bc4" opacity="0.85"/>
                        <ellipse cx="-2" cy="2" rx="2" ry="2.5" fill="#c44a8a" opacity="0.85"/>
                        <ellipse cx="2" cy="2" rx="2" ry="2.5" fill="#e89bc4" opacity="0.85"/>
                      </g>
                      <line x1="0" y1="-3.5" x2="0" y2="3.5" stroke="#222" stroke-width="0.9"/>
                    </g>
                    <g opacity="0.95">
                      <g transform="translate(28 222)"><circle r="2" fill="#ff8b6b"/><circle r="0.7" fill="#ffd56b"/></g>
                      <g transform="translate(82 230)"><circle r="1.7" fill="#ffb199"/><circle r="0.6" fill="#ffd56b"/></g>
                      <g transform="translate(238 226)"><circle r="2" fill="#e6dcff"/><circle r="0.7" fill="#ffd56b"/></g>
                      <g transform="translate(264 232)"><circle r="1.6" fill="#ffd56b"/><circle r="0.5" fill="#fff"/></g>
                    </g>
                  </svg>
                </div>
              </div>

              <!-- Sort controls -->
              <div v-if="!store.loadingSpaces && totalSpacesCount > 0" class="sort-controls-wrap">
                <div class="control-group" role="group" aria-label="Sort parks">
                  <span class="control-label">Sort by</span>
                  <div class="pill-row">
                    <button
                      v-for="opt in sortOptions"
                      :key="opt.value"
                      class="filter-pill"
                      :class="{ active: sortBy === opt.value }"
                      @click="sortBy = opt.value"
                    >
                      <svg v-if="opt.icon" viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <path :d="opt.icon"/>
                      </svg>
                      {{ opt.label }}
                    </button>
                  </div>
                </div>
              </div>

              <p v-if="!store.loadingSpaces && totalSpacesCount > 0" class="results-summary">
                Showing <strong>{{ visibleSpaces.length }}</strong> of <strong>{{ filteredSpaces.length }}</strong> parks · Sorted by <em>{{ activeSortLabel }}</em>
              </p>
            </div>

            <div v-if="store.loadingSpaces && !greenSpaces.length" class="mini-loading">
              <div class="mini-spin" aria-hidden="true"></div> Loading nearby parks…
            </div>

            <div v-else-if="filteredSpaces.length" class="spaces-grid">
              <article
                v-for="space in visibleSpaces"
                :key="space.space_id || space.space_name"
                class="space-card"
              >
                <div class="space-card-head">
                  <div class="space-icon" :class="spaceIconClass(space)">
                    <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                      <path d="M2 22c1.25-1.25 2.5-2.5 3.5-4C7 16 8 13.5 8 11c0-5.5 4.5-9 9-9 0 4.5-1 8-3.5 10.5S8.5 16 6 18c-1 1-2.5 2.5-4 4z"/>
                    </svg>
                  </div>
                  <div class="space-titles">
                    <h3 class="space-name" :style="{ fontSize: scaledPx(18) }">{{ space.space_name }}</h3>
                    <p class="space-meta-line">
                      <span class="meta-distance">
                        <svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>
                        {{ space.distance_km?.toFixed(2) }} km
                      </span>
                      <span class="meta-sep">·</span>
                      <span>{{ space.space_type || space.category || 'Open space' }}</span>
                    </p>
                  </div>
                </div>

                <div class="space-tags">
                  <span v-if="space.has_toilet_nearby" class="toilet-pill yes" title="Toilet within walking distance">
                    <svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>
                    Toilet
                  </span>
                  <span v-else class="toilet-pill no" title="No toilet within 200m">
                    <svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                    No toilet
                  </span>
                  <span v-if="space.public_access" class="info-tag access">Public access</span>
                </div>

                <div class="metric-bars">
                  <div class="metric-row">
                    <span class="metric-label">Comfort</span>
                    <div class="metric-track"><div class="metric-fill comfort" :class="comfortBarClass(space.comfort_score)" :style="{ width: `${space.comfort_score}%` }"></div></div>
                    <span class="metric-num">{{ Math.round(space.comfort_score) }}</span>
                  </div>
                  <div class="metric-row">
                    <span class="metric-label">Walkability</span>
                    <div class="metric-track"><div class="metric-fill walk" :style="{ width: `${walkPct(space.walkability_score)}%` }"></div></div>
                    <span class="metric-num">{{ walkPct(space.walkability_score) }}</span>
                  </div>
                </div>

                <p v-if="space.managed_by" class="managed-by-line">
                  <svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 21h18M5 21V7l8-4v18M19 21V11l-6-4"/></svg>
                  Managed by {{ space.managed_by }}
                </p>

                <button class="directions-btn" @click="planJourney(space)">
                  <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <polygon points="3 11 22 2 13 21 11 13 3 11"/>
                  </svg>
                  Get directions
                  <svg class="dir-arrow" viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M5 12h14M13 5l7 7-7 7"/>
                  </svg>
                </button>
              </article>
            </div>

            <div v-else-if="!store.loadingSpaces" class="filter-empty">
              <svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <p :style="{ fontSize: scaledPx(15) }">No parks found nearby. Try a different location.</p>
            </div>

            <div v-if="canShowMore" class="show-more-wrap">
              <button class="show-more-btn" @click="showAll = !showAll">
                {{ showAll ? 'Show fewer parks' : `Show all ${filteredSpaces.length} parks` }}
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"
                     :style="{ transform: showAll ? 'rotate(180deg)' : 'none' }">
                  <polyline points="6 9 12 15 18 9"/>
                </svg>
              </button>
            </div>
          </div>
        </section>

        <!-- STEP 4 · STAY CONNECTED -->
        <section id="stay-connected" class="bt-section section-light">
          <header class="bt-section-head">
            <p class="section-label"><span class="step-tag">Step 4</span> Stay connected</p>
            <h2 class="section-heading" :style="{ fontSize: scaledPx(40) }">Welcoming spaces<br><em>to drop in to.</em></h2>
            <p class="section-sub" :style="{ fontSize: scaledPx(16) }">Free, open community spaces nearby - libraries, civic buildings, visitor centres - all good places to rest, warm up, or meet someone.</p>
          </header>

          <div v-if="store.loadingWelcoming && !store.welcomingSpaces.length" class="loading-row"><div class="spinner" aria-hidden="true"></div><p :style="{ fontSize: scaledPx(15) }">Loading welcoming spaces…</p></div>
          <div v-else-if="!store.welcomingSpaces.length" class="welcoming-empty">
            <div class="welcoming-empty-card">
              <svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="#0a9b8a" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <h3 :style="{ fontSize: scaledPx(22) }">No welcoming spaces within 2 km</h3>
              <p :style="{ fontSize: scaledPx(15) }">We searched libraries, civic buildings, and visitor centres tagged in OpenStreetMap and the City of Melbourne dataset. None within walking distance of <strong>{{ store.locationLabel }}</strong>. Try a more central suburb, or check the tips below.</p>
            </div>
          </div>

          <div v-else class="welcoming-band">
            <WelcomingMap :landmarks="store.welcomingSpaces" :user-lat="store.userLat" :user-lon="store.userLon" :selected-id="selectedWelcomingId" @select="onWelcomingSelect"/>
            <div class="welcoming-legend">
              <span v-for="cat in welcomingLegend" :key="cat.name" class="legend-chip" :style="{ background: cat.bg, color: cat.fg }">
                <span class="legend-dot" :style="{ background: cat.fg }"></span>{{ cat.name }} · {{ cat.count }}
              </span>
            </div>
            <transition name="detail">
              <div v-if="selectedWelcoming" class="welcoming-detail">
                <button type="button" class="detail-close" @click="selectedWelcomingId = null" aria-label="Close details">×</button>
                <h4 class="detail-name" :style="{ fontSize: scaledPx(22) }">{{ selectedWelcoming.name }}</h4>
                <div class="detail-meta">
                  <span v-if="selectedWelcoming.sub_theme" class="detail-cat">{{ selectedWelcoming.sub_theme }}</span>
                  <span v-if="selectedWelcoming.distance_km != null" class="detail-dist">· {{ selectedWelcoming.distance_km.toFixed(2) }} km away</span>
                </div>
                <button type="button" class="detail-btn" @click="planJourney(selectedWelcoming)">
                  Get directions
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
                </button>
              </div>
            </transition>
          </div>

          <!-- Tips for first visit (verbatim) -->
          <div class="tips-band">
            <div class="tips-inner">
              <div class="tips-header">
                <p class="section-label">Helpful guidance</p>
                <h3 class="tips-heading" :style="{ fontSize: scaledPx(36) }">Tips for your<br><em>first visit</em></h3>
              </div>
              <div class="tips-grid">
                <article class="tip-card">
                  <div class="tip-icon mint"><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 8h1a4 4 0 0 1 0 8h-1"/><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg></div>
                  <h4 :style="{ fontSize: scaledPx(18) }">Go at your own pace</h4>
                  <p :style="{ fontSize: scaledPx(14) }">You don't need to join anything. Just arriving and sitting quietly is enough - these are judgment-free spaces.</p>
                </article>
                <article class="tip-card">
                  <div class="tip-icon yellow"><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div>
                  <h4 :style="{ fontSize: scaledPx(18) }">Quieter in the mornings</h4>
                  <p :style="{ fontSize: scaledPx(14) }">Libraries and community centres are usually less busy between 9am and 11am on weekdays.</p>
                </article>
                <article class="tip-card">
                  <div class="tip-icon purple"><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg></div>
                  <h4 :style="{ fontSize: scaledPx(18) }">Staff are there to help</h4>
                  <p :style="{ fontSize: scaledPx(14) }">You can always ask staff about free programs, events, or just for a chat - that's what these spaces are for.</p>
                </article>
              </div>
            </div>
          </div>
        </section>

        <footer class="page-disclaimer">
          <div class="disclaimer-inner">
            <p class="disclaimer-eyebrow">Data sources</p>
            <p :style="{ fontSize: scaledPx(13) }">Crowd patterns use the <strong>City of Melbourne pedestrian counting system</strong> (2 years of historical sensor data, 2024-2026) - coverage is limited to the CBD and inner suburbs. Live weather is from <strong>Open-Meteo</strong>. Toilets, parks, and welcoming spaces come from <strong>OpenStreetMap</strong> and the City of Melbourne Urban Forest dataset. Travel times are straight-line walking estimates.</p>
          </div>
        </footer>
      </template>
    </div>
  </MainLayout>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import { resonanceStore } from '../stores/resonanceStore'
import { uiStore } from '../stores/uiStore'
import { useResonanceApi } from '../composables/useResonanceApi'
import BestTimeLocationBar from '../components/BestTimeLocationBar.vue'
import CrowdDayChart from '../components/CrowdDayChart.vue'
import WelcomingMap from '../components/WelcomingMap.vue'

const store = resonanceStore
const api = useResonanceApi()
const route = useRoute()
const router = useRouter()
const scaledPx = (base) => `${(base * uiStore.textScale) / 100}px`

const steps = [
  { id: 'right-now',      label: 'Right now' },
  { id: 'when-you-go',    label: 'When to go' },
  { id: 'where-to-go',    label: 'Where to go' },
  { id: 'stay-connected', label: 'Stay connected' },
]
const activeSection = ref('right-now')
const SCROLL_OFFSET = 138

// True page scroll offset accounts for sticky zone (location bar + step nav)
function getStickyOffset() {
  const zone = document.querySelector('.bt-sticky-zone')
  return zone ? zone.getBoundingClientRect().height + 8 : SCROLL_OFFSET
}

let scrollSpyLocked = false
let scrollSpyUnlockTimer = null

function scrollToSection(id) {
  const el = document.getElementById(id)
  if (!el) return
  const offset = getStickyOffset()
  const y = el.getBoundingClientRect().top + window.scrollY - offset + 1
  // Lock scroll-spy briefly so the click's active state isn't overridden mid-scroll
  scrollSpyLocked = true
  if (scrollSpyUnlockTimer) clearTimeout(scrollSpyUnlockTimer)
  activeSection.value = id
  window.scrollTo({ top: y, behavior: 'smooth' })
  scrollSpyUnlockTimer = setTimeout(() => { scrollSpyLocked = false }, 850)
}

let scrollSpyHandler = null
function setupSectionObserver() {
  if (scrollSpyHandler) window.removeEventListener('scroll', scrollSpyHandler)
  // Deterministic scroll-spy: find the section whose top has crossed the trigger
  // line (just below the sticky zone). More reliable than IntersectionObserver
  // for "active step" highlighting because it picks exactly one section per
  // scroll position, with no edge-case flicker between adjacent sections.
  let rafId = null
  scrollSpyHandler = () => {
    if (scrollSpyLocked) return
    if (rafId) return
    rafId = requestAnimationFrame(() => {
      rafId = null
      const trigger = getStickyOffset() + 24
      let activeId = steps[0].id
      for (const s of steps) {
        const el = document.getElementById(s.id)
        if (!el) continue
        const top = el.getBoundingClientRect().top
        if (top <= trigger) activeId = s.id
        else break
      }
      if (activeSection.value !== activeId) activeSection.value = activeId
    })
  }
  window.addEventListener('scroll', scrollSpyHandler, { passive: true })
  scrollSpyHandler() // initial run
}
function teardownSectionObserver() {
  if (scrollSpyHandler) {
    window.removeEventListener('scroll', scrollSpyHandler)
    scrollSpyHandler = null
  }
  if (scrollSpyUnlockTimer) { clearTimeout(scrollSpyUnlockTimer); scrollSpyUnlockTimer = null }
}

const scoreError = ref(false)
const forecastFetched = ref(false)
const selectedWelcomingId = ref(null)

const hasSensorData = computed(() => {
  const bt = store.bestTimesResult
  const fc = store.forecastResult
  const btOk = bt && bt.has_sensor_data !== false && Array.isArray(bt.best_times) && bt.best_times.length > 0
  const fcOk = fc && fc.has_sensor_data !== false && fc.forecast && Object.keys(fc.forecast).length > 0
  return btOk && fcOk
})
const showNoSensorState = computed(() => forecastFetched.value && !hasSensorData.value)
const noSensorMessage = computed(() => store.bestTimesResult?.message || store.forecastResult?.message || "Our crowd forecast uses the City of Melbourne pedestrian sensor network, which covers the CBD and inner suburbs only.")

const gradeColor = computed(() => {
  const s = store.scoreResult?.resonance_score ?? 0
  if (s >= 85) return '#0a9b8a'
  if (s >= 70) return '#1d7169'
  if (s >= 50) return '#b88a00'
  return '#c44a2c'
})
const scoreArc = computed(() => Math.round((Math.max(0, Math.min(100, store.scoreResult?.resonance_score ?? 0)) / 100) * 478))
const breakdownItems = computed(() => {
  const b = store.scoreResult?.breakdown
  if (!b) return []
  return [
    { label: 'Crowd level',    value: b.crowd_score,   max: 35, color: '#0a9b8a' },
    { label: 'Weather safety', value: b.weather_score, max: 35, color: '#1d7169' },
    { label: 'Comfort',        value: b.comfort_score, max: 20, color: '#5c8a3c' },
    { label: 'Toilet access',  value: b.toilet_score,  max: 5,  color: '#b88a00' },
    { label: 'Shade',          value: b.shade_score,   max: 5,  color: '#8a6a2a' },
  ]
})
function formatPts(v) { if (v == null) return '0'; return Number.isInteger(v) ? v : v.toFixed(1) }

const goNowSpots = computed(() => store.goNowResult?.recommendations || [])
function recRingColor(s) {
  if (s >= 85) return '#0a9b8a'
  if (s >= 70) return '#1d7169'
  if (s >= 50) return '#b88a00'
  return '#c44a2c'
}
const topQuietWindow = computed(() => store.bestTimesResult?.best_times?.[0] || null)

const greenSpaces = computed(() => store.greenSpaces || [])

// ── Green spaces helpers (from previous WeekPage implementation) ──────────────
const showAll = ref(false)
const sortBy = ref('comfort')

const sortOptions = [
  { value: 'comfort',     label: 'Comfort',     icon: 'M12 2v20M2 12h20' },
  { value: 'walkability', label: 'Walkability', icon: 'M3 12h18M3 6h18M3 18h18' },
  { value: 'distance',    label: 'Distance',    icon: 'M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z' },
  { value: 'name',        label: 'Name',        icon: 'M4 6h16M4 12h16M4 18h12' },
]

const totalSpacesCount = computed(() => greenSpaces.value.length)
const toiletParksCount = computed(() => greenSpaces.value.filter(s => s.has_toilet_nearby).length)
const topComfortScore = computed(() => {
  if (!greenSpaces.value.length) return 0
  return Math.round(Math.max(...greenSpaces.value.map(s => Number(s.comfort_score) || 0)))
})

const filteredSpaces = computed(() => {
  const list = [...greenSpaces.value]
  switch (sortBy.value) {
    case 'walkability':
      list.sort((a, b) => (Number(b.walkability_score) || 0) - (Number(a.walkability_score) || 0))
      break
    case 'distance':
      list.sort((a, b) => (a.distance_km || Infinity) - (b.distance_km || Infinity))
      break
    case 'name':
      list.sort((a, b) => (a.space_name || '').localeCompare(b.space_name || ''))
      break
    case 'comfort':
    default:
      list.sort((a, b) => (Number(b.comfort_score) || 0) - (Number(a.comfort_score) || 0))
  }
  return list
})

const DEFAULT_VISIBLE = 9
const visibleSpaces = computed(() =>
  showAll.value ? filteredSpaces.value : filteredSpaces.value.slice(0, DEFAULT_VISIBLE)
)
const canShowMore = computed(() => filteredSpaces.value.length > DEFAULT_VISIBLE)
const activeSortLabel = computed(() =>
  sortOptions.find(o => o.value === sortBy.value)?.label.toLowerCase() || 'comfort'
)

function comfortBarClass(s) {
  if (s >= 70) return 'high'
  if (s >= 45) return 'mid'
  return 'low'
}

const maxWalkability = computed(() => {
  let m = 0
  for (const s of greenSpaces.value) {
    const v = Number(s.walkability_score) || 0
    if (v > m) m = v
  }
  return m || 1
})
function walkPct(score) {
  const v = Number(score) || 0
  if (v <= 0) return 0
  return Math.max(2, Math.round((v / maxWalkability.value) * 100))
}

function spaceIconClass(space) {
  const cat = (space.category || space.space_type || '').toLowerCase()
  if (cat.includes('green')) return 'green'
  if (cat.includes('leisure')) return 'leisure'
  if (cat.includes('other')) return 'neutral'
  return 'green'
}

// Reset sort/show when location changes
watch(() => [store.userLat, store.userLon], () => {
  sortBy.value = 'comfort'
  showAll.value = false
})

function planJourney(item) {
  const destLat = item.lat ?? item.latitude
  const destLon = item.lon ?? item.lng ?? item.longitude
  if (destLat == null || destLon == null) return
  router.push({
    path: '/journey',
    query: {
      from_lat: store.userLat,
      from_lon: store.userLon,
      from_name: store.locationLabel || 'My location',
      dest_lat: destLat,
      dest_lon: destLon,
      dest_name: item.space_name || item.name || 'Destination',
      auto: '1',
    },
  })
}

const selectedWelcoming = computed(() => {
  if (!selectedWelcomingId.value) return null
  return store.welcomingSpaces.find(l => l.landmark_id === selectedWelcomingId.value) || null
})
function onWelcomingSelect(id) { selectedWelcomingId.value = id }
const welcomingLegend = computed(() => {
  const seen = new Map()
  function cat(subTheme) {
    const s = (subTheme || '').toLowerCase()
    if (s.includes('library'))   return { bg: '#e6dcff', fg: '#5b3fb6', name: 'Library' }
    if (s.includes('police'))    return { bg: '#dde6f8', fg: '#2a4ab0', name: 'Police' }
    if (s.includes('fire'))      return { bg: '#ffe2d8', fg: '#c44a2c', name: 'Fire station' }
    if (s.includes('visitor'))   return { bg: '#fff3c2', fg: '#b88a00', name: 'Visitor centre' }
    if (s.includes('court'))     return { bg: '#f0e0d0', fg: '#6a3a1a', name: 'Court' }
    if (s.includes('public') || s.includes('hall')) return { bg: '#d6f4e7', fg: '#1d7169', name: 'Public building' }
    if (s.includes('health'))    return { bg: '#fce4ec', fg: '#c44a8a', name: 'Health' }
    return { bg: '#e0eedc', fg: '#4a6a4e', name: 'Community' }
  }
  for (const l of store.welcomingSpaces) {
    const c = cat(l.sub_theme)
    if (!seen.has(c.name)) seen.set(c.name, { ...c, count: 1 })
    else seen.get(c.name).count++
  }
  return Array.from(seen.values()).sort((a, b) => b.count - a.count)
})

function useCbdLocation() {
  store.setLocation(-37.8180, 144.9690, 'Melbourne CBD')
  nextTick(() => scrollToSection('when-you-go'))
}

async function loadAll() {
  if (!store.locationReady) return
  const { userLat: lat, userLon: lon } = store
  scoreError.value = false
  forecastFetched.value = false
  store.loadingScore = true
  store.loadingGoNow = true
  store.loadingForecast = true
  store.loadingSpaces = true
  store.loadingWelcoming = true

  const tasks = [
    api.fetchScore(lat, lon).then(r => { store.scoreResult = r; if (!r) scoreError.value = true }).finally(() => { store.loadingScore = false }),
    api.fetchSafety(lat, lon).then(r => { store.safetyConditions = r }),
    api.fetchGoNow(lat, lon, 2).then(r => { store.goNowResult = r }).finally(() => { store.loadingGoNow = false }),
    api.fetchBestTimes(lat, lon, 6).then(r => { store.bestTimesResult = r }),
    api.fetchForecast(lat, lon, 2).then(r => { store.forecastResult = r }).finally(() => { store.loadingForecast = false; forecastFetched.value = true }),
    api.fetchGreenSpaces(lat, lon, 2, null, 15).then(r => {
      // BE returns { green_spaces: [...] }; older shapes used `spaces` or `results`,
      // or a bare array. Check all known shapes for robustness.
      store.greenSpaces =
        r?.green_spaces ||
        r?.spaces ||
        r?.results ||
        (Array.isArray(r) ? r : []) ||
        []
    }).finally(() => { store.loadingSpaces = false }),
    api.fetchWelcomingSpaces(lat, lon, 2, 30).then(r => { store.welcomingSpaces = r?.landmarks || r?.results || (Array.isArray(r) ? r : []) }).finally(() => { store.loadingWelcoming = false }),
  ]
  await Promise.allSettled(tasks)
  setTimeout(() => setupSectionObserver(), 80)
}

watch(() => store.locationReady, (ready) => { if (ready) loadAll() })
watch(() => [store.userLat, store.userLon], () => { if (store.locationReady) loadAll() })

function applyChatbotQuery() {
  const q = route.query || {}
  if (!q.lat || !q.lon) return
  const lat = parseFloat(q.lat), lon = parseFloat(q.lon)
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) return
  if (store.userLat === lat && store.userLon === lon) return
  store.setLocation(lat, lon, q.suburb || store.locationLabel || null)
}
async function scrollToHashTarget() {
  if (!route.hash) return
  const id = route.hash.replace('#', '')
  const aliases = { 'live-score': 'right-now', 'best-spots-now': 'where-to-go', 'week-forecast': 'when-you-go', 'this-week': 'when-you-go', 'welcoming-spaces': 'stay-connected' }
  const target = aliases[id] || id
  await nextTick()
  setTimeout(() => scrollToSection(target), 200)
}
watch(() => route.hash, scrollToHashTarget)

onMounted(async () => {
  // Apply themed scrollbar to body while this page is mounted
  document.body.classList.add('bt-themed-scrollbar')
  applyChatbotQuery()
  if (store.locationReady) await loadAll()
  else setTimeout(() => setupSectionObserver(), 80)
  scrollToHashTarget()
})
onBeforeUnmount(() => {
  document.body.classList.remove('bt-themed-scrollbar')
  teardownSectionObserver()
})
</script>

<style scoped>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
.best-time-page { min-height: 100vh; background: #f7fbf4; color: #1a2e1e; font-family: system-ui,sans-serif; position: relative; }

.noise { position: fixed; inset: 0; z-index: 1000; pointer-events: none; background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E"); background-size: 180px; opacity: 0.4; }
.orb { position: fixed; border-radius: 50%; pointer-events: none; z-index: 0; filter: blur(80px); }
.orb-1 { width: 500px; height: 500px; background: rgba(90,180,110,0.16); top: -100px; left: -80px; animation: orb-drift 22s ease-in-out infinite alternate; }
.orb-2 { width: 380px; height: 380px; background: rgba(255,180,140,0.1); bottom: 10%; right: -60px; animation: orb-drift 28s ease-in-out infinite alternate-reverse; }
@keyframes orb-drift { 0%{transform:translate(0,0) scale(1)} 100%{transform:translate(40px,50px) scale(1.1)} }

.hero { position: relative; overflow: hidden; background: linear-gradient(160deg, #e4f5e0 0%, #c8edc8 100%); padding: 80px 52px 80px; border-bottom: 1px solid rgba(29,113,105,0.12); }
.hero-bg-word { position: absolute; right: -2%; top: 50%; transform: translateY(-50%); font-family: Georgia,serif; font-size: clamp(140px, 20vw, 280px); font-weight: 700; font-style: italic; color: rgba(10,155,138,0.085); white-space: nowrap; pointer-events: none; user-select: none; letter-spacing: -0.04em; }
.hero-inner { position: relative; z-index: 2; max-width: 1500px; margin: 0 auto; }
.hero-eyebrow { display: inline-flex; align-items: center; gap: 12px; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #0a9b8a; margin-bottom: 22px; }
.eyebrow-line { display: block; width: 32px; height: 1px; background: #0a9b8a; }
.hero-headline { font-family: Georgia,serif; font-size: clamp(46px, 6vw, 88px); font-weight: 700; line-height: 1.04; color: #0f1e12; margin-bottom: 18px; }
.hero-headline em { color: #0a9b8a; font-style: italic; }
.hero-sub { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.6; max-width: 720px; }

/* Sticky zone wraps the location bar + step nav so they pin together */
.bt-sticky-zone {
  position: sticky;
  top: 45px;
  z-index: 50;
  background: rgba(244, 250, 240, 0.92);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(29,113,105,0.12);
  box-shadow: 0 2px 12px rgba(10,155,138,0.04);
}
.bt-step-nav { background: transparent; border-top: 1px solid rgba(29,113,105,0.08); }
.bt-step-nav-inner { max-width: 1500px; margin: 0 auto; padding: 12px 52px; display: flex; align-items: center; gap: 8px; overflow-x: auto; scrollbar-width: none; }
.bt-step-nav-inner::-webkit-scrollbar { display: none; }
.bt-step-pill { display: inline-flex; align-items: center; gap: 10px; padding: 10px 20px 10px 10px; background: white; border: 1.5px solid rgba(29,113,105,0.12); border-radius: 999px; color: #4a6a4e; font-family: system-ui,sans-serif; font-size: 13px; font-weight: 700; cursor: pointer; white-space: nowrap; transition: all 0.2s; }
.bt-step-pill:hover { color: #0a9b8a; border-color: rgba(10,155,138,0.3); }
.bt-step-pill.active { background: linear-gradient(135deg, #0a9b8a, #056b5e); color: white; border-color: transparent; box-shadow: 0 6px 16px rgba(10,155,138,0.28); }
.bt-step-num { display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; border-radius: 50%; background: rgba(10,155,138,0.14); color: #0a9b8a; font-family: Georgia,serif; font-size: 12px; font-weight: 700; flex-shrink: 0; }
.bt-step-pill.active .bt-step-num { background: rgba(255,255,255,0.22); color: white; }

.empty-band { padding: 60px 52px 100px; }
.empty-card { display: flex; flex-direction: column; align-items: center; gap: 16px; text-align: center; max-width: 640px; margin: 0 auto; padding: 70px 40px; background: white; border: 1px solid rgba(29,113,105,0.12); border-radius: 24px; box-shadow: 0 8px 28px rgba(0,0,0,0.04); }
.empty-card h3 { font-family: Georgia,serif; color: #0f1e12; font-weight: 700; }
.empty-card p { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.6; }
.empty-tip { background: #fff8e0; border: 1px solid #ffe89a; padding: 12px 18px; border-radius: 12px; color: #6a5300; line-height: 1.55; text-align: left; margin-top: 10px; max-width: 520px; }

.bt-section { position: relative; z-index: 1; }
.section-light { background: transparent; }
.section-mint  { background: linear-gradient(180deg, rgba(228,245,224,0.4) 0%, rgba(247,251,244,1) 100%); }
.section-cream { background: linear-gradient(180deg, rgba(250,248,240,0.7) 0%, rgba(244,248,232,0.5) 100%); }
.bt-section + .bt-section { border-top: 1px solid rgba(29,113,105,0.08); }
.bt-section-head { max-width: 1500px; margin: 0 auto; padding: 60px 52px 28px; }
.section-label { font-family: system-ui,sans-serif; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #0a9b8a; margin-bottom: 16px; display: inline-flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.step-tag { display: inline-flex; align-items: center; padding: 3px 11px; background: #0a9b8a; color: white; border-radius: 999px; font-weight: 800; letter-spacing: 0.05em; font-size: 11px; }
.data-source-pill { display: inline-flex; padding: 3px 10px; background: #fff3c2; border: 1px solid #e8c860; color: #8a6000; border-radius: 999px; font-size: 10px; font-weight: 800; letter-spacing: 0.04em; }
.section-heading { font-family: Georgia,serif; font-weight: 700; line-height: 1.06; color: #0f1e12; margin-bottom: 14px; }
.section-heading em { color: #0a9b8a; font-style: italic; }
.section-sub { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.65; max-width: 760px; }

.loading-row, .data-error, .empty-inline { max-width: 1500px; margin: 0 auto; padding: 40px 52px 60px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; color: #4a6a4e; text-align: center; }
.empty-inline p { font-family: system-ui,sans-serif; max-width: 560px; line-height: 1.6; }
.spinner { width: 28px; height: 28px; border-radius: 50%; border: 3px solid rgba(10,155,138,0.16); border-top-color: #0a9b8a; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.data-error p { font-family: system-ui,sans-serif; color: #6a5300; background: #fff8e0; border: 1px solid #ffe89a; padding: 14px 22px; border-radius: 12px; }

.dashboard-band { max-width: 1500px; margin: 0 auto; padding: 16px 52px 50px; }
.dashboard-inner { display: grid; grid-template-columns: 260px 1fr 340px; gap: 48px; align-items: start; }
.dash-label { font-family: system-ui,sans-serif; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #0a9b8a; margin-bottom: 20px; }
.dash-score { display: flex; flex-direction: column; align-items: center; gap: 16px; }
.ring-wrap { position: relative; width: 200px; height: 200px; }
.ring { width: 100%; height: 100%; transform: rotate(-90deg); }
.ring-track { fill: none; stroke: #e8f2e8; stroke-width: 14; }
.ring-fill { fill: none; stroke-width: 14; stroke-linecap: round; transition: stroke-dasharray 0.9s cubic-bezier(0.22,1,0.36,1), stroke 0.4s; }
.ring-text { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; }
.ring-num { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; line-height: 1; }
.ring-out { font-family: system-ui,sans-serif; color: #6a8e6e; font-weight: 600; }
.grade-pill { padding: 7px 16px; border-radius: 999px; color: white; font-family: system-ui,sans-serif; font-weight: 800; text-transform: uppercase; letter-spacing: 0.06em; }
.dash-breakdown { min-width: 0; }
.bar-row { display: flex; align-items: center; gap: 14px; margin-bottom: 14px; }
.bar-label { width: 130px; font-family: system-ui,sans-serif; font-weight: 700; color: #1a2e1e; flex-shrink: 0; }
.bar-track { flex: 1; height: 11px; background: #eaf4ea; border-radius: 999px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 999px; transition: width 0.7s cubic-bezier(0.22,1,0.36,1); }
.bar-pts { width: 60px; font-family: system-ui,sans-serif; font-weight: 700; color: #1a2e1e; text-align: right; }
.bar-max { color: #8aaa8e; font-weight: 500; }
.weather-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.weather-tile { display: flex; flex-direction: column; align-items: center; gap: 3px; padding: 16px 12px; background: white; border: 1px solid rgba(10,155,138,0.12); border-radius: 12px; color: #1d7169; }
.w-num { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; line-height: 1; }
.w-label { font-family: system-ui,sans-serif; color: #6a8e6e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }

.safety-strip { padding: 16px 52px; border-top: 1px solid rgba(29,113,105,0.08); border-bottom: 1px solid rgba(29,113,105,0.08); }
.safety-inner { max-width: 1500px; margin: 0 auto; display: flex; align-items: flex-start; gap: 12px; }
.safety-dot { width: 10px; height: 10px; border-radius: 50%; background: currentColor; flex-shrink: 0; margin-top: 6px; }
.safety-strip p { font-family: system-ui,sans-serif; line-height: 1.55; }
.safety-strip strong { font-weight: 800; }
.verdict-good    { background: #e8f8f5; color: #0a6e62; }
.verdict-caution { background: #fff8e0; color: #8a6000; }
.verdict-poor    { background: #ffeaea; color: #c44a2c; }
.verdict-unknown { background: #f0f0f8; color: #4a6a4e; }

.week-band { max-width: 1500px; margin: 0 auto; padding: 0 52px 70px; }
.best-window-banner { display: flex; align-items: center; gap: 16px; padding: 18px 22px; margin-bottom: 26px; background: linear-gradient(135deg, #0a9b8a 0%, #1d7169 100%); border-radius: 16px; color: white; box-shadow: 0 12px 28px rgba(10,155,138,0.2); }
.bw-star { font-size: 28px; line-height: 1; }
.bw-content { flex: 1; }
.bw-eyebrow { font-family: system-ui,sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; opacity: 0.85; margin-bottom: 4px; }
.bw-line { font-family: system-ui,sans-serif; font-size: 15px; line-height: 1.5; }
.week-split { display: grid; grid-template-columns: 1.5fr 1fr; gap: 32px; align-items: start; }
.week-col-label { font-family: system-ui,sans-serif; font-size: 12px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: #0a9b8a; margin-bottom: 10px; }
.week-chart-card, .week-summary-card { background: white; border: 1px solid rgba(29,113,105,0.14); border-radius: 18px; padding: 24px 26px; box-shadow: 0 8px 24px rgba(10,155,138,0.06); }
.chart-foot { color: #6a8e6e; margin-top: 12px; line-height: 1.5; font-family: system-ui,sans-serif; }
.summary-hint { color: #4a6a4e; margin-bottom: 18px; font-family: system-ui,sans-serif; line-height: 1.5; }
.quiet-list { list-style: none; display: flex; flex-direction: column; gap: 10px; }
.quiet-row { display: flex; align-items: flex-start; gap: 14px; padding: 14px 16px; background: #fafbf6; border: 1px solid rgba(29,113,105,0.1); border-radius: 12px; }
.quiet-row-best { background: linear-gradient(135deg, #f0faf0 0%, white 60%); border-color: #0a9b8a; box-shadow: 0 4px 14px rgba(10,155,138,0.1); }
.quiet-rank { position: relative; min-width: 32px; height: 32px; border-radius: 50%; background: #e8f2e8; color: #0f1e12; font-family: Georgia,serif; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.quiet-row-best .quiet-rank { background: #0a9b8a; color: white; }
.quiet-rank-tag { position: absolute; top: -8px; left: 50%; transform: translateX(-50%); padding: 1px 7px; background: #0a9b8a; color: white; font-family: system-ui,sans-serif; font-size: 8px; font-weight: 800; letter-spacing: 0.06em; border-radius: 999px; text-transform: uppercase; }
.quiet-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 4px; }
.quiet-day { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; line-height: 1.15; }
.quiet-hour { font-family: system-ui,sans-serif; color: #4a6a4e; font-weight: 600; }
.quiet-meta { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-top: 2px; }
.crowd-pip { padding: 2px 9px; border-radius: 999px; font-family: system-ui,sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 0.03em; text-transform: uppercase; }
.crowd-pip.crowd-low      { background: #d6f4e7; color: #1d7169; }
.crowd-pip.crowd-moderate { background: #fff3c2; color: #8a6000; }
.crowd-pip.crowd-high     { background: #ffded5; color: #c44a2c; }
.crowd-pip.crowd-unknown  { background: #f0f0f8; color: #6a8e6e; }
.quiet-count { font-family: system-ui,sans-serif; font-size: 12px; color: #6a8e6e; font-weight: 600; }

.no-sensor-band { max-width: 1500px; margin: 0 auto; padding: 20px 52px 70px; }
.no-sensor-card { max-width: 720px; margin: 0 auto; padding: 40px 36px; background: white; border: 1.5px solid #ffe89a; border-radius: 20px; display: flex; flex-direction: column; align-items: center; gap: 14px; text-align: center; box-shadow: 0 12px 32px rgba(184,138,0,0.08); }
.no-sensor-card h3 { font-family: Georgia,serif; color: #0f1e12; font-weight: 700; }
.no-sensor-card p { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.6; max-width: 560px; }
.no-sensor-actions { display: flex; gap: 12px; flex-wrap: wrap; justify-content: center; margin-top: 8px; }
.no-sensor-btn { display: inline-flex; align-items: center; gap: 8px; padding: 12px 22px; border-radius: 12px; font-family: system-ui,sans-serif; font-size: 14px; font-weight: 700; cursor: pointer; border: 1.5px solid transparent; transition: all 0.2s; }
.no-sensor-btn.primary { background: linear-gradient(135deg, #0a9b8a, #056b5e); color: white; box-shadow: 0 8px 20px rgba(10,155,138,0.25); }
.no-sensor-btn.primary:hover { transform: translateY(-2px); }
.no-sensor-btn.outline { background: white; color: #0a9b8a; border-color: rgba(10,155,138,0.3); }
.no-sensor-btn.outline:hover { background: #f0faf0; }

.spots-wrap { max-width: 1500px; margin: 0 auto; padding: 0 52px 50px; display: flex; flex-direction: column; gap: 32px; }
.featured-card { position: relative; background: linear-gradient(135deg, #f0faf0 0%, white 60%); border: 1.5px solid rgba(10,155,138,0.25); border-radius: 24px; padding: 36px; box-shadow: 0 24px 60px rgba(10,155,138,0.12); display: flex; flex-direction: column; gap: 18px; }
.featured-card::before { content: ''; position: absolute; left: 0; top: 24px; bottom: 24px; width: 5px; border-radius: 0 4px 4px 0; background: linear-gradient(180deg, #b88a00, #f5c812); }
.featured-head { display: flex; justify-content: space-between; align-items: center; gap: 24px; flex-wrap: wrap; }
.featured-title-block { flex: 1; min-width: 240px; }
.rank-eyebrow { display: inline-flex; align-items: center; gap: 10px; font-family: system-ui,sans-serif; font-size: 12px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: #0a9b8a; margin-bottom: 10px; }
.rank-circle { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 50%; background: #0a9b8a; color: white; font-family: Georgia,serif; font-size: 14px; }
.featured-name { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; line-height: 1.05; margin-bottom: 10px; }
.featured-meta { display: inline-flex; align-items: center; gap: 10px; font-family: system-ui,sans-serif; font-size: 14px; color: #4a6a4e; font-weight: 600; flex-wrap: wrap; }
.featured-meta svg { color: #0a9b8a; }
.grade-chip { padding: 3px 10px; border-radius: 999px; font-family: system-ui,sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 0.05em; text-transform: uppercase; }
.grade-excellent { background: #d6f4e7; color: #0a6e62; }
.grade-good      { background: #e8f5f0; color: #1d7169; }
.grade-fair      { background: #fff8e0; color: #8a6000; }
.grade-poor      { background: #ffeaea; color: #c44a2c; }
.featured-score-ring { position: relative; width: 130px; height: 130px; flex-shrink: 0; }
.featured-score-ring .ring { width: 100%; height: 100%; transform: rotate(-90deg); }
.featured-score-ring .ring-track { fill: none; stroke: rgba(184,138,0,0.18); stroke-width: 10; }
.featured-score-ring .ring-fill { fill: none; stroke-width: 10; stroke-linecap: round; transition: stroke-dasharray 0.9s cubic-bezier(0.22,1,0.36,1), stroke 0.4s; }
.featured-score-ring .score-num { font-family: Georgia,serif; font-weight: 700; color: #0a9b8a; line-height: 1; }
.featured-score-ring .score-out { font-family: system-ui,sans-serif; font-size: 11px; color: #6a8e6e; font-weight: 600; margin-top: 2px; }
.featured-why { padding: 16px 20px; background: rgba(10,155,138,0.06); border-radius: 14px; color: #1a2e1e; line-height: 1.55; font-family: system-ui,sans-serif; }
.featured-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.info-tag { display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; border-radius: 999px; font-family: system-ui,sans-serif; font-size: 13px; font-weight: 700; }
.info-tag.crowd-low      { background: #d6f4e7; color: #1d7169; }
.info-tag.crowd-moderate { background: #fff3c2; color: #b88a00; }
.info-tag.crowd-high     { background: #ffded5; color: #c44a2c; }
.info-tag.crowd-unknown  { background: #f0f0f8; color: #6a8e6e; }
.info-tag.tag-toilet    { background: #d6f4e7; color: #1d7169; }
.info-tag.tag-no-toilet { background: #ffe8d8; color: #a04a1a; }
.featured-actions { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 4px; }
.get-there-btn { display: inline-flex; align-items: center; justify-content: center; gap: 10px; padding: 14px 26px; border-radius: 13px; font-family: system-ui,sans-serif; font-size: 15px; font-weight: 700; cursor: pointer; transition: all 0.25s; border: none; text-decoration: none; }
.get-there-btn.primary { background: linear-gradient(135deg, #0a9b8a, #056b5e); color: white; box-shadow: 0 12px 28px rgba(10,155,138,0.3); }
.get-there-btn.primary:hover { transform: translateY(-2px); box-shadow: 0 16px 34px rgba(10,155,138,0.4); }
.get-there-btn.outline { background: white; color: #0a9b8a; border: 1.5px solid rgba(10,155,138,0.3); }
.get-there-btn.outline:hover { background: #0a9b8a; color: white; }
.get-there-btn.small { padding: 10px 18px; font-size: 13px; }

.runners-band {}
.runners-heading { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; margin-bottom: 16px; }
.runners-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.runner-card { background: white; border: 1px solid rgba(29,113,105,0.12); border-radius: 18px; padding: 26px 28px; display: flex; flex-direction: column; gap: 10px; transition: transform 0.2s, box-shadow 0.2s; }
.runner-card:hover { transform: translateY(-2px); box-shadow: 0 14px 32px rgba(10,155,138,0.1); }
.runner-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.runner-rank { width: 30px; height: 30px; border-radius: 50%; background: #e8f2e8; color: #0f1e12; font-family: Georgia,serif; font-weight: 700; display: flex; align-items: center; justify-content: center; font-size: 16px; }
.runner-name { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; line-height: 1.15; }
.runner-meta { font-family: system-ui,sans-serif; font-size: 13px; color: #6a8e6e; font-weight: 600; }
.runner-score-strip { display: flex; align-items: center; gap: 10px; }
.runner-score-num { font-family: Georgia,serif; font-weight: 700; color: #0a9b8a; font-size: 26px; line-height: 1; }
.runner-score-bar { flex: 1; height: 8px; background: #eaf4ea; border-radius: 999px; overflow: hidden; }
.bar-inner { display: block; height: 100%; background: linear-gradient(90deg, #0a9b8a, #1d7169); border-radius: 999px; transition: width 0.7s; }
.runner-why { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.5; }
.runner-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.info-tag-sm { padding: 3px 9px; border-radius: 999px; font-family: system-ui,sans-serif; font-size: 11px; font-weight: 700; }
.info-tag-sm.crowd-low      { background: #d6f4e7; color: #1d7169; }
.info-tag-sm.crowd-moderate { background: #fff3c2; color: #b88a00; }
.info-tag-sm.crowd-high     { background: #ffded5; color: #c44a2c; }
.info-tag-sm.crowd-unknown  { background: #f0f0f8; color: #6a8e6e; }
.info-tag-sm.tag-toilet     { background: #d6f4e7; color: #1d7169; }

.spaces-wrap { max-width: 1500px; margin: 20px auto 0; padding: 40px 52px 70px; border-top: 1px solid rgba(29,113,105,0.08); }
.stats-strip { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin-bottom: 50px; }
.stat-card-big { display: flex; flex-direction: column; align-items: flex-start; gap: 12px; padding: 30px 28px; background: white; border: 1px solid rgba(29,113,105,0.12); border-radius: 18px; box-shadow: 0 10px 24px rgba(10,155,138,0.06); transition: transform 0.25s, box-shadow 0.25s; }
.stat-card-big:hover { transform: translateY(-3px); box-shadow: 0 16px 36px rgba(10,155,138,0.14); }
.stat-icon-big { width: 56px; height: 56px; border-radius: 16px; display: flex; align-items: center; justify-content: center; position: relative; }
.stat-icon-big::before { content: ''; position: absolute; inset: -4px; border: 1.5px solid currentColor; border-radius: 18px; opacity: 0.18; }
.stat-icon-big.mint   { background: #d6f4e7; color: #1d7169; }
.stat-icon-big.purple { background: #e6dcff; color: #5b3fb6; }
.stat-icon-big.yellow { background: #fff3c2; color: #b88a00; }
.stat-num-big { font-family: Georgia,serif; font-weight: 700; color: #0a9b8a; line-height: 1; letter-spacing: -0.02em; }
.stat-label-big { font-family: system-ui,sans-serif; font-size: 12px; font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase; color: #4a6a4e; }

.spaces-header { display: grid; grid-template-columns: 1fr 320px; gap: 36px; align-items: center; margin-bottom: 28px; }
.spaces-eyebrow { margin-bottom: 14px; }
.spaces-heading { font-family: Georgia,serif; font-weight: 700; line-height: 1.06; color: #0f1e12; margin-bottom: 14px; }
.spaces-heading em { color: #0a9b8a; font-style: italic; }
.spaces-sub { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.65; }

.park-scene { width: 100%; max-width: 320px; border-radius: 14px; overflow: hidden; box-shadow: 0 12px 28px rgba(10,155,138,0.12); }
.park-scene svg { display: block; width: 100%; height: auto; }
.park-cloud-a { animation: cloud-drift-a 16s ease-in-out infinite alternate; }
.park-cloud-b { animation: cloud-drift-b 22s ease-in-out infinite alternate; }
.park-bird { animation: bird-fly 9s linear infinite; }
.park-person { animation: person-walk 6s ease-in-out infinite alternate; transform-origin: center; }
.park-tree-a { animation: tree-sway 7s ease-in-out infinite alternate; transform-origin: 43px 130px; }
.park-tree-b { animation: tree-sway 9s ease-in-out infinite alternate-reverse; transform-origin: 235px 130px; }
@keyframes cloud-drift-a { 0%{transform:translateX(0)} 100%{transform:translateX(18px)} }
@keyframes cloud-drift-b { 0%{transform:translateX(0)} 100%{transform:translateX(-22px)} }
@keyframes bird-fly { 0%{transform:translate(-60px,4px)} 50%{transform:translate(40px,-10px)} 100%{transform:translate(140px,4px)} }
@keyframes person-walk { 0%{transform:translateX(-8px)} 100%{transform:translateX(10px)} }
@keyframes tree-sway { 0%{transform:rotate(-1deg)} 100%{transform:rotate(1.5deg)} }

.sort-controls { display: inline-flex; align-items: center; gap: 12px; padding: 10px 18px; background: #fffbe9; border: 1px solid rgba(184,138,0,0.18); border-radius: 14px; margin-bottom: 14px; }
.sort-label { font-family: system-ui,sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: #6a5300; }
.sort-pills { display: flex; gap: 6px; flex-wrap: wrap; }
.sort-pill { display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; background: white; border: 1px solid rgba(29,113,105,0.12); border-radius: 999px; color: #4a6a4e; font-family: system-ui,sans-serif; font-size: 12px; font-weight: 700; cursor: pointer; transition: all 0.2s; }
.sort-pill:hover { color: #0a9b8a; border-color: rgba(10,155,138,0.3); }
.sort-pill.active { background: linear-gradient(135deg, #0a9b8a, #056b5e); color: white; border-color: transparent; box-shadow: 0 6px 16px rgba(10,155,138,0.28); }
.results-summary { font-family: system-ui,sans-serif; font-size: 13px; color: #6a8e6e; margin-bottom: 26px; }
.results-summary strong { color: #0a9b8a; font-weight: 800; }
.results-summary em { color: #1a2e1e; font-style: italic; font-weight: 700; }

.spaces-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
.space-card { background: white; border: 1px solid rgba(29,113,105,0.12); border-radius: 18px; padding: 24px 26px; display: flex; flex-direction: column; gap: 14px; transition: transform 0.2s, box-shadow 0.2s; }
.space-card:hover { transform: translateY(-2px); box-shadow: 0 14px 32px rgba(10,155,138,0.1); }
.space-card-head { display: flex; align-items: center; gap: 14px; }
.space-icon { width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.space-icon.green { background: #d6f4e7; color: #1d7169; }
.space-titles { flex: 1; min-width: 0; }
.space-name { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; line-height: 1.15; }
.space-meta-line { display: inline-flex; align-items: center; gap: 6px; font-family: system-ui,sans-serif; font-size: 12px; color: #6a8e6e; font-weight: 600; margin-top: 3px; }
.meta-sep { color: #c0c8c0; }

.space-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.toilet-pill { padding: 3px 10px; border-radius: 999px; font-family: system-ui,sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; }
.toilet-pill.yes { background: #d6f4e7; color: #1d7169; }
.toilet-pill.no  { background: #ffe8d8; color: #a04a1a; }
.info-tag-tiny { padding: 3px 10px; background: #e6dcff; color: #5b3fb6; border-radius: 999px; font-family: system-ui,sans-serif; font-size: 11px; font-weight: 700; letter-spacing: 0.03em; text-transform: uppercase; }

.metric-bars { display: flex; flex-direction: column; gap: 8px; }
.metric-row { display: flex; align-items: center; gap: 10px; font-family: system-ui,sans-serif; }
.metric-label { width: 80px; font-size: 11px; font-weight: 800; color: #6a8e6e; letter-spacing: 0.04em; text-transform: uppercase; flex-shrink: 0; }
.metric-track { flex: 1; height: 8px; background: #eaf4ea; border-radius: 999px; overflow: hidden; }
.metric-fill { display: block; height: 100%; border-radius: 999px; transition: width 0.7s; }
.metric-fill.comfort-high { background: linear-gradient(90deg, #0a9b8a, #1d7169); }
.metric-fill.comfort-mid  { background: linear-gradient(90deg, #b88a00, #c8a040); }
.metric-fill.comfort-low  { background: linear-gradient(90deg, #c44a2c, #d8714a); }
.metric-fill.walk         { background: linear-gradient(90deg, #5b3fb6, #7a5fc8); }
.metric-num { width: 32px; font-size: 13px; font-weight: 700; color: #0f1e12; text-align: right; }

.managed-by-line { display: inline-flex; align-items: center; gap: 6px; font-family: system-ui,sans-serif; font-size: 12px; color: #8aaa8e; font-weight: 600; }

.directions-btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 11px 18px; background: linear-gradient(135deg, #0a9b8a, #056b5e); color: white; border: none; border-radius: 11px; font-family: system-ui,sans-serif; font-size: 13px; font-weight: 700; cursor: pointer; box-shadow: 0 8px 20px rgba(10,155,138,0.25); transition: all 0.2s; }
.directions-btn:hover { transform: translateY(-1px); box-shadow: 0 12px 26px rgba(10,155,138,0.35); }

.show-more-wrap { display: flex; justify-content: center; margin-top: 28px; }
.show-more-btn { padding: 12px 28px; background: white; border: 1.5px solid rgba(10,155,138,0.3); color: #0a9b8a; border-radius: 12px; font-family: system-ui,sans-serif; font-weight: 700; font-size: 14px; cursor: pointer; transition: all 0.2s; }
.show-more-btn:hover { background: #f0faf0; }

.welcoming-band { max-width: 1500px; margin: 0 auto; padding: 0 52px 60px; }
.welcoming-empty { padding: 30px 52px 70px; }
.welcoming-empty-card { max-width: 720px; margin: 0 auto; padding: 36px 32px; background: white; border: 1px solid rgba(29,113,105,0.14); border-radius: 18px; display: flex; flex-direction: column; align-items: center; gap: 12px; text-align: center; box-shadow: 0 12px 28px rgba(10,155,138,0.08); }
.welcoming-empty-card h3 { font-family: Georgia,serif; color: #0f1e12; font-weight: 700; }
.welcoming-empty-card p { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.6; max-width: 560px; }

.welcoming-legend { display: flex; flex-wrap: wrap; gap: 8px; margin: 18px 0; }
.legend-chip { display: inline-flex; align-items: center; gap: 7px; padding: 5px 12px; border-radius: 999px; font-family: system-ui,sans-serif; font-size: 12px; font-weight: 700; }
.legend-dot { width: 8px; height: 8px; border-radius: 50%; }
.welcoming-detail { position: relative; padding: 24px 30px; background: white; border: 1.5px solid rgba(10,155,138,0.22); border-radius: 18px; box-shadow: 0 12px 32px rgba(10,155,138,0.12); display: flex; flex-direction: column; gap: 12px; max-width: 760px; }
.detail-close { position: absolute; top: 14px; right: 14px; width: 28px; height: 28px; border-radius: 50%; background: white; border: 1px solid rgba(29,113,105,0.18); color: #6a8e6e; font-size: 20px; line-height: 1; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.detail-close:hover { color: #c44a2c; border-color: #c44a2c; }
.detail-name { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; line-height: 1.15; padding-right: 36px; }
.detail-meta { display: flex; align-items: center; gap: 4px; font-family: system-ui,sans-serif; font-size: 13px; color: #6a8e6e; font-weight: 600; flex-wrap: wrap; }
.detail-cat { padding: 3px 10px; border-radius: 999px; background: #d6f4e7; color: #1d7169; }
.detail-btn { align-self: flex-start; display: inline-flex; align-items: center; gap: 8px; padding: 11px 22px; background: linear-gradient(135deg, #0a9b8a, #056b5e); color: white; border-radius: 11px; font-family: system-ui,sans-serif; font-size: 13px; font-weight: 700; text-decoration: none; box-shadow: 0 8px 20px rgba(10,155,138,0.25); }
.detail-btn:hover { transform: translateY(-1px); }
.detail-enter-active, .detail-leave-active { transition: opacity 0.25s, transform 0.25s; }
.detail-enter-from, .detail-leave-to { opacity: 0; transform: translateY(6px); }

.tips-band { background: linear-gradient(180deg, #edf7ec 0%, #d6e8d8 100%); padding: 80px 52px; margin-top: 60px; border-radius: 24px 24px 0 0; }
.tips-inner { max-width: 1500px; margin: 0 auto; }
.tips-header { text-align: center; margin-bottom: 36px; }
.tips-header .section-label { display: inline-flex; }
.tips-heading { font-family: Georgia,serif; font-weight: 700; line-height: 1.06; color: #0f1e12; margin-top: 14px; }
.tips-heading em { color: #1d7169; font-style: italic; }
.tips-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.tip-card { background: white; padding: 30px 28px; border-radius: 18px; box-shadow: 0 12px 28px rgba(10,155,138,0.08); border: 1px solid rgba(29,113,105,0.08); display: flex; flex-direction: column; gap: 12px; }
.tip-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.tip-icon.mint   { background: #d6f4e7; color: #1d7169; }
.tip-icon.yellow { background: #fff3c2; color: #b88a00; }
.tip-icon.purple { background: #e6dcff; color: #5b3fb6; }
.tip-card h4 { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; }
.tip-card p { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.6; }

/* Green spaces — empty state when no parks in dataset for this location */
.green-spaces-wrap { max-width: 1500px; margin: 20px auto 0; padding: 40px 52px 70px; border-top: 1px solid rgba(29,113,105,0.08); }
.green-empty-band { display: flex; justify-content: center; padding: 30px 0; }
.green-empty-card { max-width: 720px; padding: 40px 36px; background: linear-gradient(180deg, #f0faf0 0%, white 60%); border: 1.5px solid rgba(10,155,138,0.22); border-radius: 20px; display: flex; flex-direction: column; align-items: center; gap: 14px; text-align: center; box-shadow: 0 12px 32px rgba(10,155,138,0.08); }
.green-empty-icon { width: 64px; height: 64px; border-radius: 18px; background: #d6f4e7; display: flex; align-items: center; justify-content: center; }
.green-empty-card h3 { font-family: Georgia,serif; color: #0f1e12; font-weight: 700; }
.green-empty-card p { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.65; max-width: 560px; }
.green-empty-card em { color: #0a9b8a; font-style: italic; font-weight: 600; }
.green-empty-actions { display: flex; gap: 12px; flex-wrap: wrap; justify-content: center; margin-top: 8px; }
.green-empty-btn { display: inline-flex; align-items: center; gap: 8px; padding: 12px 22px; border-radius: 12px; font-family: system-ui,sans-serif; font-size: 14px; font-weight: 700; cursor: pointer; border: 1.5px solid transparent; transition: all 0.2s; }
.green-empty-btn.primary { background: linear-gradient(135deg, #0a9b8a, #056b5e); color: white; box-shadow: 0 8px 20px rgba(10,155,138,0.25); }
.green-empty-btn.primary:hover { transform: translateY(-2px); }
.green-empty-btn.outline { background: white; color: #0a9b8a; border-color: rgba(10,155,138,0.3); }
.green-empty-btn.outline:hover { background: #f0faf0; }

.page-disclaimer { background: #1d2820; color: rgba(255,255,255,0.78); padding: 40px 52px; }
.disclaimer-inner { max-width: 1500px; margin: 0 auto; }
.disclaimer-eyebrow { font-family: system-ui,sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; color: #6dcec0; margin-bottom: 10px; }
.page-disclaimer p { font-family: system-ui,sans-serif; line-height: 1.65; max-width: 1000px; }
.page-disclaimer strong { color: white; font-weight: 700; }

@media (max-width: 1200px) {
  .dashboard-inner { grid-template-columns: 220px 1fr; }
  .dash-weather { grid-column: 1 / -1; }
  .week-split { grid-template-columns: 1fr; }
  .runners-grid { grid-template-columns: 1fr 1fr; }
  .spaces-grid { grid-template-columns: repeat(2, 1fr); }
  .spaces-header { grid-template-columns: 1fr; }
  .park-scene { max-width: 360px; justify-self: start; }
  .tips-grid { grid-template-columns: 1fr; }
}
@media (max-width: 760px) {
  .hero { padding: 60px 20px 50px; }
  .bt-step-nav-inner { padding: 8px 16px; }
  .empty-band, .no-sensor-band, .welcoming-empty { padding: 30px 20px 60px; }
  .bt-section-head { padding: 40px 20px 16px; }
  .dashboard-band, .spots-wrap, .spaces-wrap, .green-spaces-wrap, .week-band, .welcoming-band { padding-left: 20px; padding-right: 20px; }
  .dashboard-inner { grid-template-columns: 1fr; gap: 32px; }
  .dash-score { align-items: flex-start; }
  .safety-strip { padding: 14px 20px; }
  .featured-card { padding: 24px; }
  .runners-grid { grid-template-columns: 1fr; }
  .stats-strip { grid-template-columns: 1fr; }
  .spaces-grid { grid-template-columns: 1fr; }
  .tips-band { padding: 50px 20px; }
  .page-disclaimer { padding: 32px 20px; }
}

/* ═══════════════════════════════════════════════════════════════════════════
   GREEN SPACES BAND — full inline implementation from the previous WeekPage
   (kept exactly to preserve the visual design the user wants restored)
   ═══════════════════════════════════════════════════════════════════════════ */
.spaces-band {
  background: white;
  padding: 90px 52px;
  border-top: 1px solid rgba(29,113,105,0.08);
}
.spaces-inner { max-width: 1500px; margin: 0 auto; }

/* 3-card stats strip (above title) */
.spaces-band > .spaces-inner > .stats-strip {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 22px;
  margin-bottom: 50px;
}
.spaces-band .stat-card-big {
  display: flex; flex-direction: column; align-items: flex-start; gap: 12px;
  padding: 36px 32px;
  background: white;
  border: 1px solid rgba(29,113,105,0.14);
  border-radius: 22px;
  box-shadow: 0 8px 24px rgba(10,155,138,0.06);
  transition: transform 0.3s, box-shadow 0.3s;
}
.spaces-band .stat-card-big:hover { transform: translateY(-3px); box-shadow: 0 16px 36px rgba(10,155,138,0.14); }
.spaces-band .stat-icon-big {
  width: 64px; height: 64px; border-radius: 18px;
  display: flex; align-items: center; justify-content: center;
  position: relative;
}
.spaces-band .stat-icon-big::before { content: ''; position: absolute; inset: -4px; border: 1.5px solid currentColor; border-radius: 18px; opacity: 0.18; }
.spaces-band .stat-icon-big.mint   { background: #d6f4e7; color: #1d7169; }
.spaces-band .stat-icon-big.purple { background: #e6dcff; color: #5b3fb6; }
.spaces-band .stat-icon-big.yellow { background: #fff3c2; color: #b88a00; }
.spaces-band .stat-num-big { font-family: Georgia,serif; font-weight: 700; color: #0a9b8a; line-height: 1; letter-spacing: -0.02em; }
.spaces-band .stat-label-big { font-family: system-ui,sans-serif; font-size: 13px; font-weight: 800; color: #4a6a4e; letter-spacing: 0.08em; text-transform: uppercase; }

/* Title + animation grid */
.spaces-band-header { margin-bottom: 36px; }
.title-with-animation {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 40px;
  align-items: center;
  margin-bottom: 36px;
}
.spaces-band-title { max-width: 760px; }
.spaces-band-title .section-label { font-family: system-ui,sans-serif; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #0a9b8a; margin-bottom: 14px; }
.spaces-band-title .section-heading { font-family: Georgia,serif; font-weight: 700; line-height: 1.06; color: #0f1e12; margin-bottom: 14px; }
.spaces-band-title .section-heading em { color: #0a9b8a; font-style: italic; }
.spaces-band-title .section-sub { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.65; }

/* Park animation */
.park-animation {
  width: 100%;
  max-width: 360px;
  justify-self: end;
  border-radius: 20px;
  overflow: hidden;
  background: linear-gradient(180deg, #e0f5e8, #f0faf0);
  border: 1px solid rgba(29,113,105,0.1);
  box-shadow: 0 12px 28px rgba(10,155,138,0.08);
}
.park-svg { display: block; width: 100%; height: auto; }
.park-sun { animation: gs-sun-rays 16s linear infinite; transform-box: fill-box; }
@keyframes gs-sun-rays { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.park-cloud.c1 { animation: gs-cloud-1 24s ease-in-out infinite alternate; }
.park-cloud.c2 { animation: gs-cloud-2 30s ease-in-out infinite alternate-reverse; }
@keyframes gs-cloud-1 { 0% { transform: translateX(-20px); } 100% { transform: translateX(40px); } }
@keyframes gs-cloud-2 { 0% { transform: translateX(0); } 100% { transform: translateX(-30px); } }
.park-bird.b1 { animation: gs-bird-1 14s linear infinite; }
.park-bird.b2 { animation: gs-bird-2 18s linear infinite; }
@keyframes gs-bird-1 { 0% { transform: translate(-30px, 80px); } 100% { transform: translate(360px, 50px); } }
@keyframes gs-bird-2 { 0% { transform: translate(360px, 100px); } 100% { transform: translate(-30px, 70px); } }
.park-tree.t-left  { animation: gs-tree-sway 4.5s ease-in-out infinite alternate; }
.park-tree.t-right { animation: gs-tree-sway-2 5.5s ease-in-out infinite alternate-reverse; }
@keyframes gs-tree-sway   { 0% { transform: rotate(-1.5deg); } 100% { transform: rotate(1.5deg); } }
@keyframes gs-tree-sway-2 { 0% { transform: rotate(1deg); }    100% { transform: rotate(-1deg); } }
.park-person { animation: gs-person-bounce 1.6s ease-in-out infinite; }
@keyframes gs-person-bounce { 0%, 100% { transform: translate(190px, 215px); } 50% { transform: translate(190px, 213px); } }
.arm-wave { animation: gs-arm-wave 2.4s ease-in-out infinite; transform-box: fill-box; }
@keyframes gs-arm-wave { 0%, 100% { transform: rotate(0deg); } 50% { transform: rotate(15deg); } }
.park-butterfly { animation: gs-butterfly-fly 12s ease-in-out infinite; transform-box: fill-box; }
@keyframes gs-butterfly-fly {
  0%   { transform: translate(80px, 130px); }
  25%  { transform: translate(140px, 100px); }
  50%  { transform: translate(200px, 140px); }
  75%  { transform: translate(150px, 120px); }
  100% { transform: translate(80px, 130px); }
}
.bf-wings { animation: gs-bf-flap 0.32s ease-in-out infinite alternate; transform-box: fill-box; transform-origin: center; }
@keyframes gs-bf-flap { 0% { transform: scaleX(1); } 100% { transform: scaleX(0.45); } }

/* Sort controls (centered) */
.sort-controls-wrap {
  display: flex; justify-content: center;
  margin: 0 auto 14px;
  padding: 14px 22px;
  background: #faf8f0;
  border: 1px solid rgba(29,113,105,0.1);
  border-radius: 16px;
  width: fit-content;
}
.control-group { display: flex; align-items: center; gap: 16px; }
.control-label { font-family: system-ui,sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: #6a8e6e; }
.pill-row { display: flex; flex-wrap: wrap; gap: 6px; }
.filter-pill {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 9px 16px;
  background: white; border: 1.5px solid rgba(29,113,105,0.18);
  border-radius: 999px;
  font-family: system-ui,sans-serif; font-size: 13px; font-weight: 700;
  color: #4a6a4e; cursor: pointer;
  transition: all 0.2s;
}
.filter-pill:hover { border-color: #0a9b8a; color: #0a9b8a; }
.filter-pill.active {
  background: linear-gradient(135deg, #0a9b8a, #056b5e); color: white; border-color: #0a9b8a;
  box-shadow: 0 4px 12px rgba(10,155,138,0.28);
}

.spaces-band .results-summary {
  text-align: center;
  font-family: system-ui,sans-serif; font-size: 13px; color: #6a8e6e; font-weight: 500;
  margin-top: 8px;
}
.spaces-band .results-summary strong { color: #0a9b8a; font-weight: 800; }
.spaces-band .results-summary em { color: #1a2e1e; font-style: italic; font-weight: 700; }

.mini-loading { display: flex; align-items: center; justify-content: center; gap: 10px; color: #6a8e6e; font-family: system-ui,sans-serif; font-weight: 600; padding: 30px 0; }
.mini-spin { width: 18px; height: 18px; border-radius: 50%; border: 2px solid rgba(10,155,138,0.2); border-top-color: #0a9b8a; animation: gs-spin 0.7s linear infinite; }
@keyframes gs-spin { to { transform: rotate(360deg); } }

/* Spaces grid + cards */
.spaces-band .spaces-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}
.spaces-band .space-card {
  display: flex; flex-direction: column; gap: 16px;
  padding: 24px 22px;
  background: white;
  border: 1px solid rgba(29,113,105,0.12);
  border-radius: 18px;
  transition: transform 0.25s, box-shadow 0.25s, border-color 0.25s;
}
.spaces-band .space-card:hover { transform: translateY(-3px); box-shadow: 0 16px 36px rgba(10,155,138,0.12); border-color: rgba(10,155,138,0.3); }
.spaces-band .space-card-head { display: flex; align-items: flex-start; gap: 14px; }
.spaces-band .space-icon { width: 46px; height: 46px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.spaces-band .space-icon.green   { background: #d6f4e7; color: #1d7169; }
.spaces-band .space-icon.leisure { background: #fff3c2; color: #8a6000; }
.spaces-band .space-icon.neutral { background: #f0f0f8; color: #4a6a4e; }
.spaces-band .space-titles { flex: 1; min-width: 0; }
.spaces-band .space-name { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; line-height: 1.2; margin-bottom: 4px; }
.spaces-band .space-meta-line { display: inline-flex; align-items: center; gap: 6px; flex-wrap: wrap; font-family: system-ui,sans-serif; font-size: 13px; color: #6a8e6e; font-weight: 600; }
.spaces-band .meta-distance { display: inline-flex; align-items: center; gap: 5px; }
.spaces-band .meta-distance svg { color: #0a9b8a; }
.spaces-band .meta-sep { color: #c5d6c7; }
.spaces-band .space-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.spaces-band .toilet-pill {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 3px 10px; border-radius: 999px;
  font-family: system-ui,sans-serif; font-size: 11px; font-weight: 800;
  letter-spacing: 0.04em; text-transform: uppercase;
  white-space: nowrap;
}
.spaces-band .toilet-pill.yes { background: #d6f4e7; color: #0a6e62; }
.spaces-band .toilet-pill.no  { background: #f5e4dc; color: #a04a1a; }
.spaces-band .info-tag.access { background: #e8e8ff; color: #2a2ab0; padding: 3px 10px; border-radius: 999px; font-family: system-ui,sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; }

.spaces-band .metric-bars { display: flex; flex-direction: column; gap: 8px; }
.spaces-band .metric-row { display: grid; grid-template-columns: 86px 1fr 38px; gap: 10px; align-items: center; }
.spaces-band .metric-label { font-family: system-ui,sans-serif; font-size: 11px; font-weight: 700; color: #6a8e6e; letter-spacing: 0.04em; text-transform: uppercase; }
.spaces-band .metric-track { height: 6px; background: #eaf4ea; border-radius: 999px; overflow: hidden; }
.spaces-band .metric-fill { height: 100%; border-radius: 999px; transition: width 0.6s cubic-bezier(0.22,1,0.36,1); }
.spaces-band .metric-fill.comfort.high { background: linear-gradient(90deg, #0a9b8a, #1d7169); }
.spaces-band .metric-fill.comfort.mid  { background: linear-gradient(90deg, #d4a854, #b88a00); }
.spaces-band .metric-fill.comfort.low  { background: #c44a2c; }
.spaces-band .metric-fill.walk         { background: linear-gradient(90deg, #5b3fb6, #8a6dd1); }
.spaces-band .metric-num { font-family: Georgia,serif; font-size: 14px; font-weight: 700; color: #0f1e12; text-align: right; }
.spaces-band .managed-by-line {
  display: inline-flex; align-items: center; gap: 6px;
  font-family: system-ui,sans-serif; font-size: 12px; color: #8aaa8e; font-weight: 500;
  padding-top: 10px; border-top: 1px solid rgba(29,113,105,0.08);
}
.spaces-band .managed-by-line svg { color: #0a9b8a; }
.spaces-band .directions-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  width: 100%; padding: 12px 18px;
  background: linear-gradient(135deg, #0a9b8a, #056b5e);
  color: white; border: none; border-radius: 12px;
  font-family: system-ui,sans-serif; font-size: 14px; font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 8px 20px rgba(10,155,138,0.28);
  margin-top: auto;
}
.spaces-band .directions-btn:hover { transform: translateY(-2px); box-shadow: 0 14px 28px rgba(10,155,138,0.4); }
.spaces-band .directions-btn .dir-arrow { transition: transform 0.25s; }
.spaces-band .directions-btn:hover .dir-arrow { transform: translateX(3px); }

.filter-empty {
  display: flex; flex-direction: column; align-items: center; gap: 12px;
  padding: 60px 40px; text-align: center;
  background: #f6faf3; border: 1px dashed rgba(29,113,105,0.25);
  border-radius: 18px; color: #6a8e6e;
}
.filter-empty svg { color: #0a9b8a; }
.filter-empty p { font-family: system-ui,sans-serif; }

.spaces-band .show-more-wrap { display: flex; justify-content: center; margin-top: 24px; }
.spaces-band .show-more-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  padding: 14px 28px;
  background: white; border: 1.5px dashed rgba(10,155,138,0.4); color: #0a9b8a;
  border-radius: 14px; cursor: pointer;
  font-family: system-ui,sans-serif; font-size: 14px; font-weight: 700;
  transition: all 0.2s;
}
.spaces-band .show-more-btn:hover { background: #0a9b8a; color: white; border-color: #0a9b8a; border-style: solid; }
.spaces-band .show-more-btn svg { transition: transform 0.25s; }

@media (max-width: 1300px) {
  .title-with-animation { grid-template-columns: 1fr 280px; }
}
@media (max-width: 1100px) {
  .title-with-animation { grid-template-columns: 1fr; }
  .park-animation { justify-self: center; max-width: 320px; }
}
@media (max-width: 980px) {
  .spaces-band { padding: 60px 20px; }
  .spaces-band > .spaces-inner > .stats-strip { grid-template-columns: 1fr; }
  .spaces-band .stat-card-big { padding: 28px 24px; align-items: center; text-align: center; }
  .spaces-band .spaces-grid { grid-template-columns: 1fr; }
  .sort-controls-wrap { width: 100%; padding: 14px 16px; }
  .control-group { flex-direction: column; align-items: flex-start; gap: 10px; width: 100%; }
  .pill-row { width: 100%; }
  .filter-pill { flex: 1; justify-content: center; }
  .spaces-band .metric-row { grid-template-columns: 70px 1fr 30px; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
</style>

<!-- Unscoped style for the BODY scrollbar — applied only while this page is
     mounted (the script adds/removes `bt-themed-scrollbar` on document.body). -->
<style>
body.bt-themed-scrollbar {
  /* Firefox: thin themed scrollbar */
  scrollbar-color: #0a9b8a #e8f5ed;
  scrollbar-width: thin;
}
body.bt-themed-scrollbar::-webkit-scrollbar { width: 12px; height: 12px; }
body.bt-themed-scrollbar::-webkit-scrollbar-track {
  background: #e8f5ed;
  border-left: 1px solid rgba(29,113,105,0.1);
}
body.bt-themed-scrollbar::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #0a9b8a 0%, #056b5e 100%);
  border-radius: 999px;
  border: 2px solid #e8f5ed;
  background-clip: padding-box;
  min-height: 40px;
}
body.bt-themed-scrollbar::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #1d7169 0%, #034a40 100%);
  background-clip: padding-box;
}
body.bt-themed-scrollbar::-webkit-scrollbar-corner { background: #e8f5ed; }
</style>