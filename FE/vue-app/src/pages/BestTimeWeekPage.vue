<template>
  <div class="week-page">
    <div class="noise" aria-hidden="true"></div>
    <div class="orb orb-1" aria-hidden="true"></div>
    <div class="orb orb-2" aria-hidden="true"></div>

    <BestTimeLocationBar />

    <section class="hero">
      <div class="hero-bg-word" aria-hidden="true">FORECAST</div>
      <div class="hero-inner">
        <RouterLink to="/best-time" class="back-btn">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
          Back to live score
        </RouterLink>
        <p class="hero-eyebrow"><span class="eyebrow-line"></span>Your 7-day resonance forecast</p>
        <h1 class="hero-headline">Your best windows<br><em>this week.</em></h1>
        <p class="hero-sub" :style="{ fontSize: scaledPx(18) }">
          Built from 2 years of City of Melbourne pedestrian sensor data. Find quieter windows for outings.
        </p>
      </div>

      <div v-if="store.locationReady && quietestDay" class="best-window-callout">
        <div class="bw-icon">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        </div>
        <div class="bw-text">
          <p class="bw-label">Best window this week</p>
          <p class="bw-main"><strong>{{ quietestDay.day }} at {{ formatHour(quietestDay.hour) }}</strong> - your quietest moment.</p>
        </div>
        <RouterLink to="/best-time/now" class="bw-btn">
          Find best spots
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
        </RouterLink>
      </div>
    </section>

    <section v-if="!store.locationReady" class="empty-band">
      <div class="empty-card">
        <h3 :style="{ fontSize: scaledPx(24) }">Set your location to see your forecast</h3>
        <p :style="{ fontSize: scaledPx(16) }">Use the location bar above to set your suburb, then your 7-day heatmap will appear here.</p>
      </div>
    </section>

    <template v-else>
      <section v-if="store.loadingForecast && !store.forecastResult" class="loading-band">
        <div class="big-spinner" aria-hidden="true"></div>
        <p :style="{ fontSize: scaledPx(18) }">Building your week forecast…</p>
      </section>

      <template v-else-if="store.forecastResult">
        <!-- ═══ HEATMAP ═══ -->
        <section class="heatmap-band" data-reveal>
          <div class="heatmap-inner">
            <div class="heatmap-header">
              <p class="section-label">Crowd heatmap</p>
              <h2 class="section-heading" :style="{ fontSize: scaledPx(40) }">
                Crowd heatmap<br><em>this week.</em>
              </h2>
              <p class="section-sub" :style="{ fontSize: scaledPx(15) }">
                Each cell is one hour, 8am - 8pm. Hover for details - tap a cell to pin it below.
              </p>
            </div>

            <div class="heatmap-wrap">
              <div class="heat-grid axis-row">
                <div class="day-spacer"></div>
                <span v-for="h in displayHours" :key="`hh-${h}`" class="hour-label">{{ formatHour(h) }}</span>
              </div>

              <div v-for="day in forecastDays" :key="day" class="heat-grid day-row">
                <div class="day-label">{{ day.slice(0, 3) }}</div>
                <button
                  v-for="h in displayHours"
                  :key="`${day}-${h}`"
                  class="heat-cell"
                  :style="cellStyle(day, h)"
                  :class="{ 'cell-selected': isSelected(day, h), 'cell-best': isBestCell(day, h) }"
                  :aria-label="`${day} ${formatHour(h)} ${getHourData(day, h)?.crowd_level || 'unknown'}`"
                  @click="selectCell(day, h)"
                  @mouseenter="showTooltip($event, day, h)"
                  @mouseleave="hideTooltip"
                  @focus="showTooltip($event, day, h)"
                  @blur="hideTooltip"
                >
                  <span v-if="isBestCell(day, h)" class="best-star" aria-hidden="true">
                    <svg viewBox="0 0 24 24" width="11" height="11" fill="white" stroke="white" stroke-width="0.5" aria-hidden="true"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                  </span>
                </button>
              </div>

              <div class="legend-row">
                <div class="day-spacer"></div>
                <div class="legend-content">
                  <span class="legend-label">Quietest</span>
                  <div class="legend-bar"></div>
                  <span class="legend-label">Busiest</span>
                </div>
              </div>
            </div>

            <div v-if="selectedCell" class="cell-detail">
              <div class="cd-icon">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              </div>
              <div class="cd-text">
                <span class="cd-when">{{ selectedCell.day }}, {{ formatHour(selectedCell.hour) }}</span>
                <span class="cd-meta">
                  <span class="crowd-badge" :class="`crowd-${selectedCell.level.toLowerCase()}`">{{ selectedCell.level }}</span>
                  <span class="cd-count">~{{ selectedCell.avg_count }} people/hr</span>
                </span>
              </div>
              <RouterLink to="/best-time/now" class="cd-plan-btn">
                Plan this visit
                <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
              </RouterLink>
              <button class="cd-close" @click="selectedCell = null" aria-label="Close detail">
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
            </div>
            <p v-if="store.forecastResult.data_note" class="data-note">{{ store.forecastResult.data_note }}</p>
          </div>
        </section>

        <!-- ═══ HEATMAP TOOLTIP ═══ -->
        <Teleport to="body">
          <transition name="tip-fade">
            <div
              v-if="hoveredCell"
              class="heat-tooltip"
              :style="{ left: `${hoveredCell.x}px`, top: `${hoveredCell.y}px` }"
              role="tooltip"
            >
              <div class="tip-when">{{ hoveredCell.day }}, {{ formatHour(hoveredCell.hour) }}</div>
              <div class="tip-meta">
                <span class="crowd-badge tip-badge" :class="`crowd-${hoveredCell.level.toLowerCase()}`">{{ hoveredCell.level }}</span>
                <span class="tip-count">~{{ hoveredCell.count }} people/hr</span>
              </div>
              <div class="tip-arrow"></div>
            </div>
          </transition>
        </Teleport>

        <!-- ═══ CREAM BAND: Quietest day + Full-width stat cards ═══ -->
        <section class="cream-band" data-reveal>
          <div class="cream-inner">
            <div class="quietest-card-wrap" v-if="quietestDay">
              <div class="quietest-card">
                <div class="qd-content">
                  <p class="card-label">Quietest day this week</p>
                  <h3 class="qd-day" :style="{ fontSize: scaledPx(48) }">{{ quietestDay.day }}</h3>
                  <p class="qd-best">Best from {{ formatHour(quietestDay.hour) }}</p>
                </div>
                <div class="qd-aside">
                  <div class="qd-stats">
                    <span class="crowd-badge crowd-low">Low crowd</span>
                    <span class="qd-count">~{{ quietestDay.avg_count }} people/hr</span>
                  </div>
                  <RouterLink to="/best-time/now" class="qd-cta">
                    Find quiet spots near me
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
                  </RouterLink>
                </div>
              </div>
            </div>

            <!-- Full-width stat cards strip -->
            <div class="stats-strip">
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
          </div>
        </section>

        <!-- ═══ FULL-WIDTH GREEN SPACES BAND ═══ -->
        <section class="spaces-band" data-reveal>
          <div class="spaces-inner">
            <div class="spaces-band-header">
              <div class="title-with-animation">
                <div class="spaces-band-title">
                  <p class="section-label">Comfortable parks near you</p>
                  <h2 class="section-heading" :style="{ fontSize: scaledPx(40) }">
                    Green spaces<br><em>ranked &amp; filtered.</em>
                  </h2>
                  <p class="section-sub" :style="{ fontSize: scaledPx(15) }">
                    Comfort score combines walkability, shade, and toilet access. Walkability scores are normalised
                    against the highest in your search area.
                  </p>
                </div>

                <!-- ─── Mini park scene animation ─── -->
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

                    <!-- Sky -->
                    <rect width="320" height="180" fill="url(#psky)"/>

                    <!-- Sun with rotating rays -->
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

                    <!-- Drifting clouds -->
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

                    <!-- Birds flying -->
                    <g class="park-bird b1" fill="none" stroke="#2d5a3d" stroke-width="1.5" stroke-linecap="round">
                      <path d="M0 0 q3-4 6 0 q3-4 6 0"/>
                    </g>
                    <g class="park-bird b2" fill="none" stroke="#2d5a3d" stroke-width="1.3" stroke-linecap="round">
                      <path d="M0 0 q2.5-3 5 0 q2.5-3 5 0"/>
                    </g>

                    <!-- Hills -->
                    <path d="M0 160 Q80 130 160 152 T320 145 L320 200 L0 200Z" fill="#a8d8a8" opacity="0.7"/>

                    <!-- Grass / ground -->
                    <path d="M0 178 L320 178 L320 240 L0 240 Z" fill="url(#pgrass)"/>

                    <!-- Path -->
                    <path d="M-20 240 Q120 218 160 212 Q200 218 340 240" stroke="#d4b87a" stroke-width="22" fill="none" stroke-linecap="round" opacity="0.85"/>
                    <path d="M-20 240 Q120 218 160 212 Q200 218 340 240" stroke="#e4cfa0" stroke-width="14" fill="none" stroke-linecap="round"/>

                    <!-- Tree left (sways gently) -->
                    <g class="park-tree t-left" style="transform-origin: 50px 195px">
                      <rect x="47" y="170" width="6" height="32" fill="#5a3a1a"/>
                      <circle cx="50" cy="166" r="22" fill="#3e8a4a"/>
                      <circle cx="38" cy="160" r="14" fill="#5cb471"/>
                      <circle cx="62" cy="162" r="14" fill="#4fae6b"/>
                      <circle cx="50" cy="148" r="12" fill="#6cc481"/>
                    </g>

                    <!-- Tree right -->
                    <g class="park-tree t-right" style="transform-origin: 280px 200px">
                      <rect x="278" y="178" width="5" height="26" fill="#5a3a1a"/>
                      <circle cx="280" cy="174" r="17" fill="#3e8a4a"/>
                      <circle cx="271" cy="170" r="11" fill="#5cb471"/>
                      <circle cx="289" cy="172" r="11" fill="#4fae6b"/>
                    </g>

                    <!-- Bench -->
                    <g transform="translate(110 200)">
                      <rect x="-22" y="-8" width="44" height="3" fill="#6b4226" rx="1"/>
                      <rect x="-22" y="-3" width="44" height="3" fill="#6b4226" rx="1"/>
                      <rect x="-20" y="0" width="3" height="10" fill="#6b4226"/>
                      <rect x="17" y="0" width="3" height="10" fill="#6b4226"/>
                    </g>

                    <!-- Walking person (bounces gently) -->
                    <g class="park-person" transform="translate(190 215)">
                      <ellipse cx="0" cy="6" rx="8" ry="1.5" fill="#000" opacity="0.15"/>
                      <g class="person-body">
                        <!-- Legs -->
                        <rect class="leg-back" x="-2" y="-4" width="3" height="9" rx="1.5" fill="#234"/>
                        <rect class="leg-front" x="-1" y="-4" width="3" height="9" rx="1.5" fill="#345"/>
                        <!-- Body -->
                        <path d="M-6-15 Q-7-7 -5-3 L5-3 Q7-7 6-15 Q3-17 0-17 Q-3-17 -6-15Z" fill="#0a9b8a"/>
                        <!-- Arm -->
                        <g class="arm-wave" style="transform-origin: 5px -13px">
                          <rect x="4" y="-13" width="2.5" height="9" rx="1.2" fill="#0a9b8a"/>
                          <circle cx="5" cy="-3" r="1.5" fill="#f0c8a0"/>
                        </g>
                        <!-- Other arm -->
                        <rect x="-7" y="-13" width="2.5" height="9" rx="1.2" fill="#0a9b8a"/>
                        <circle cx="-5.5" cy="-3" r="1.5" fill="#f0c8a0"/>
                        <!-- Head -->
                        <rect x="-1.5" y="-19" width="3" height="3" fill="#f0c8a0"/>
                        <circle cx="0" cy="-22" r="5.5" fill="#f0c8a0"/>
                        <path d="M-5.5-22 Q-5-29 0-29 Q5-29 5.5-22 Q3-26 0-25 Q-3-26 -5.5-22Z" fill="#3a2010"/>
                      </g>
                    </g>

                    <!-- Butterfly (flutters) -->
                    <g class="park-butterfly">
                      <g class="bf-wings">
                        <ellipse cx="-2" cy="-1" rx="2.5" ry="3.5" fill="#c44a8a" opacity="0.85"/>
                        <ellipse cx="2" cy="-1" rx="2.5" ry="3.5" fill="#e89bc4" opacity="0.85"/>
                        <ellipse cx="-2" cy="2" rx="2" ry="2.5" fill="#c44a8a" opacity="0.85"/>
                        <ellipse cx="2" cy="2" rx="2" ry="2.5" fill="#e89bc4" opacity="0.85"/>
                      </g>
                      <line x1="0" y1="-3.5" x2="0" y2="3.5" stroke="#222" stroke-width="0.9"/>
                    </g>

                    <!-- Flowers -->
                    <g opacity="0.95">
                      <g transform="translate(28 222)"><circle r="2" fill="#ff8b6b"/><circle r="0.7" fill="#ffd56b"/></g>
                      <g transform="translate(82 230)"><circle r="1.7" fill="#ffb199"/><circle r="0.6" fill="#ffd56b"/></g>
                      <g transform="translate(238 226)"><circle r="2" fill="#e6dcff"/><circle r="0.7" fill="#ffd56b"/></g>
                      <g transform="translate(264 232)"><circle r="1.6" fill="#ffd56b"/><circle r="0.5" fill="#fff"/></g>
                    </g>
                  </svg>
                </div>
              </div>

              <!-- Centered sort controls (no filter) -->
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
                      <component :is="'svg'" v-if="opt.icon" viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <path :d="opt.icon"/>
                      </component>
                      {{ opt.label }}
                    </button>
                  </div>
                </div>
              </div>

              <p v-if="!store.loadingSpaces && totalSpacesCount > 0" class="results-summary">
                Showing
                <strong>{{ visibleSpaces.length }}</strong>
                of <strong>{{ filteredSpaces.length }}</strong>
                parks · Sorted by <em>{{ activeSortLabel }}</em>
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

                <!-- Get directions button -->
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
      </template>

      <section v-else class="empty-band">
        <div class="empty-card">
          <h3 :style="{ fontSize: scaledPx(24) }">No forecast data available</h3>
          <p :style="{ fontSize: scaledPx(16) }">No pedestrian sensors found near this location. Try a suburb closer to Melbourne CBD.</p>
        </div>
      </section>

      <section class="bottom-nav-band">
        <div class="bottom-nav-inner">
          <RouterLink to="/best-time" class="bnav-btn">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
            Live score
          </RouterLink>
          <RouterLink to="/best-time/now" class="bnav-btn primary">
            Best spots now
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
          </RouterLink>
          <RouterLink to="/welcoming-spaces" class="bnav-btn">
            Welcoming spaces
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
          </RouterLink>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { resonanceStore } from '../stores/resonanceStore'
import { uiStore } from '../stores/uiStore'
import { useResonanceApi } from '../composables/useResonanceApi'
import BestTimeLocationBar from '../components/BestTimeLocationBar.vue'

const store = resonanceStore
const router = useRouter()
const { fetchForecast, fetchGreenSpaces } = useResonanceApi()
const scaledPx = (base) => `${(base * uiStore.textScale) / 100}px`

// ── Heatmap state ────────────────────────────────────
const selectedCell = ref(null)
const hoveredCell  = ref(null)
const displayHours = Array.from({ length: 13 }, (_, i) => i + 8)

const forecastDays = computed(() => store.forecastResult?.forecast_days ?? [])

function formatHour(h) {
  const ampm = h < 12 ? 'am' : 'pm'
  const h12  = h % 12 === 0 ? 12 : h % 12
  return `${h12}${ampm}`
}
function getHourData(day, hour) { return store.forecastResult?.forecast?.[day]?.[hour] ?? null }
function isSelected(day, hour) { return selectedCell.value?.day === day && selectedCell.value?.hour === hour }
function selectCell(day, hour) {
  const d = getHourData(day, hour)
  if (!d) return
  if (isSelected(day, hour)) { selectedCell.value = null; return }
  selectedCell.value = { day, hour, level: d.crowd_level, avg_count: Math.round(d.avg_count) }
}
function isBestCell(day, hour) { return quietestDay.value?.day === day && quietestDay.value?.hour === hour }

function showTooltip(event, day, hour) {
  const d = getHourData(day, hour)
  if (!d) return
  const target = event.currentTarget || event.target
  const rect = target.getBoundingClientRect()
  hoveredCell.value = {
    day, hour,
    level: d.crowd_level,
    count: Math.round(d.avg_count),
    x: rect.left + rect.width / 2,
    y: rect.top - 12,
  }
}
function hideTooltip() { hoveredCell.value = null }

const maxCount = computed(() => {
  let m = 1
  for (const day of forecastDays.value) {
    for (const h of displayHours) {
      const d = getHourData(day, h)
      if (d && d.avg_count > m) m = d.avg_count
    }
  }
  return m
})
function countToColor(count) {
  const t = Math.min(count / maxCount.value, 1)
  const stops = [
    [10, 110, 98], [86, 154, 102], [212, 168, 84], [196, 110, 76], [156, 60, 50],
  ]
  const seg = t * (stops.length - 1)
  const lo = Math.floor(seg), hi = Math.min(lo + 1, stops.length - 1), f = seg - lo
  const [r1,g1,b1] = stops[lo], [r2,g2,b2] = stops[hi]
  return {
    r: Math.round(r1 + (r2 - r1) * f),
    g: Math.round(g1 + (g2 - g1) * f),
    b: Math.round(b1 + (b2 - b1) * f),
  }
}
function cellStyle(day, hour) {
  const d = getHourData(day, hour)
  if (!d) return { background: '#eaf4ea' }
  const { r, g, b } = countToColor(d.avg_count)
  return { background: `rgb(${r},${g},${b})` }
}
const quietestDay = computed(() => {
  const f = store.forecastResult?.forecast
  if (!f) return null
  let best = null
  for (const day of forecastDays.value) {
    for (const h of displayHours) {
      const d = f[day]?.[h]
      if (!d || d.crowd_level !== 'Low') continue
      if (!best || d.avg_count < best.avg_count) {
        best = { day, hour: h, avg_count: Math.round(d.avg_count) }
      }
    }
  }
  return best
})

// ── Green spaces (filter removed; sort only) ─────────
const showAll = ref(false)
const sortBy = ref('comfort')

const sortOptions = [
  { value: 'comfort',     label: 'Comfort',     icon: 'M12 2v20M2 12h20' },
  { value: 'walkability', label: 'Walkability', icon: 'M3 12h18M3 6h18M3 18h18' },
  { value: 'distance',    label: 'Distance',    icon: 'M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z' },
  { value: 'name',        label: 'Name',        icon: 'M4 6h16M4 12h16M4 18h12' },
]

const greenSpaces = computed(() => store.greenSpaces || [])
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

function planJourney(space) {
  const lat = space.lat ?? space.latitude
  const lon = space.lon ?? space.lng ?? space.longitude
  if (lat == null || lon == null) return
  router.push({
    path: '/journey',
    query: {
      from_lat: store.userLat,
      from_lon: store.userLon,
      from_name: store.locationLabel || 'My location',
      dest_lat: lat,
      dest_lon: lon,
      dest_name: space.name,
      auto: '1'                  // ← triggers auto-search on arrival
    }
  })
}

// ── Reset sort/show on location change ───────────────
watch(() => [store.userLat, store.userLon], () => {
  sortBy.value = 'comfort'
  showAll.value = false
})

// ── Data loading ─────────────────────────────────────
async function loadAll() {
  if (!store.locationReady) return
  const { userLat: lat, userLon: lon } = store
  store.loadingForecast = true
  store.loadingSpaces = true
  selectedCell.value = null
  showAll.value = false
  try {
    const [forecast, spacesResp] = await Promise.all([
      fetchForecast(lat, lon, 2),
      fetchGreenSpaces(lat, lon, 2, null, 15),
    ])
    store.forecastResult = forecast
    store.greenSpaces =
      spacesResp?.green_spaces ||
      spacesResp?.results ||
      (Array.isArray(spacesResp) ? spacesResp : []) ||
      []
  } finally {
    store.loadingForecast = false
    store.loadingSpaces = false
    setTimeout(setupReveal, 80)
  }
}

watch(() => store.locationReady, (r) => { if (r) loadAll() })
watch(() => [store.userLat, store.userLon], () => { if (store.locationReady) loadAll() })

let revealObserver = null
function setupReveal() {
  if (revealObserver) revealObserver.disconnect()
  revealObserver = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) e.target.classList.add('in-view') }), { threshold: 0.1 })
  document.querySelectorAll('[data-reveal]').forEach(el => revealObserver.observe(el))
}

onMounted(() => {
  setupReveal()
  if (store.locationReady) loadAll()
})
onBeforeUnmount(() => {
  if (revealObserver) revealObserver.disconnect()
  hoveredCell.value = null
})
</script>

<style scoped>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
.week-page { min-height: 100vh; background: #f2faf0; color: #1a2e1e; font-family: system-ui, sans-serif; position: relative; overflow-x: hidden; }
.noise { position: fixed; inset: 0; z-index: 1000; pointer-events: none; background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E"); background-size: 180px; opacity: 0.45; }
.orb { position: fixed; border-radius: 50%; pointer-events: none; z-index: 0; filter: blur(80px); }
.orb-1 { width: 500px; height: 500px; background: rgba(90,180,110,0.18); top: -100px; left: -80px; animation: orb-drift 22s ease-in-out infinite alternate; }
.orb-2 { width: 380px; height: 380px; background: rgba(255,180,140,0.12); bottom: 5%; right: -60px; animation: orb-drift 28s ease-in-out infinite alternate-reverse; }
@keyframes orb-drift { 0%{transform:translate(0,0) scale(1)} 100%{transform:translate(40px,50px) scale(1.1)} }

.hero { position: relative; overflow: hidden; background: linear-gradient(160deg, #c8edc8 0%, #056b5e 100%); padding: 220px 52px 140px; color: white; }
.hero-bg-word { position: absolute; right: -2%; top: 50%; transform: translateY(-50%); font-family: Georgia,serif; font-size: clamp(140px, 20vw, 280px); font-weight: 700; font-style: italic; color: rgba(255,255,255,0.08); white-space: nowrap; pointer-events: none; user-select: none; letter-spacing: -0.04em; }
.hero-inner { position: relative; z-index: 2; max-width: 1500px; margin: 0 auto; }
.back-btn { display: inline-flex; align-items: center; gap: 8px; padding: 8px 18px; background: rgba(255,255,255,0.18); border: 1px solid rgba(255,255,255,0.25); border-radius: 999px; color: white; font-size: 13px; font-weight: 700; text-decoration: none; margin-bottom: 24px; transition: background 0.2s; }
.back-btn:hover { background: rgba(255,255,255,0.28); }
.hero-eyebrow { display: inline-flex; align-items: center; gap: 12px; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: rgba(255,255,255,0.85); margin-bottom: 22px; }
.eyebrow-line { display: block; width: 32px; height: 1px; background: rgba(255,255,255,0.85); }
.hero-headline { font-family: Georgia,serif; font-size: clamp(46px, 6vw, 88px); font-weight: 700; line-height: 1.04; color: white; margin-bottom: 16px; }
.hero-headline em { color: #f5c812; font-style: italic; }
.hero-sub { font-family: system-ui,sans-serif; color: rgba(255,255,255,0.88); line-height: 1.6; max-width: 640px; }

.best-window-callout { position: absolute; bottom: -40px; right: 52px; z-index: 5; display: flex; align-items: center; gap: 16px; background: white; border-radius: 18px; padding: 18px 22px; box-shadow: 0 24px 60px rgba(0,0,0,0.18); max-width: 620px; }
.bw-icon { width: 44px; height: 44px; border-radius: 12px; background: #fff3c2; color: #b88a00; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; }
.bw-text { flex: 1; min-width: 0; }
.bw-label { font-family: system-ui,sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: #b88a00; margin-bottom: 4px; }
.bw-main { font-family: system-ui,sans-serif; font-size: 14px; color: #1a2e1e; line-height: 1.45; }
.bw-main strong { font-family: Georgia,serif; font-size: 16px; color: #0a9b8a; font-weight: 700; }
.bw-btn { display: inline-flex; align-items: center; gap: 7px; padding: 11px 18px; background: linear-gradient(135deg, #0a9b8a, #056b5e); color: white; border-radius: 12px; font-family: system-ui,sans-serif; font-size: 13px; font-weight: 700; text-decoration: none; flex-shrink: 0; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 8px 20px rgba(10,155,138,0.32); }
.bw-btn:hover { transform: translateY(-2px); box-shadow: 0 12px 28px rgba(10,155,138,0.42); }

.empty-band, .loading-band { padding: 100px 52px 80px; }
.empty-card { display: flex; flex-direction: column; align-items: center; gap: 12px; text-align: center; max-width: 600px; margin: 0 auto; padding: 60px 40px; background: white; border: 1px solid rgba(29,113,105,0.12); border-radius: 24px; box-shadow: 0 8px 28px rgba(0,0,0,0.04); }
.empty-card h3 { font-family: Georgia,serif; color: #0f1e12; font-weight: 700; }
.empty-card p { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.6; }
.loading-band { display: flex; flex-direction: column; align-items: center; gap: 18px; }
.big-spinner { width: 44px; height: 44px; border-radius: 50%; border: 4px solid rgba(10,155,138,0.18); border-top-color: #0a9b8a; animation: spin 0.8s linear infinite; }
.loading-band p { font-family: system-ui,sans-serif; color: #4a6a4e; font-weight: 600; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Heatmap */
.heatmap-band { background: white; padding: 90px 52px; border-bottom: 1px solid rgba(29,113,105,0.1); opacity: 0; transform: translateY(40px); transition: all 0.9s cubic-bezier(0.22,1,0.36,1); }
.heatmap-band.in-view { opacity: 1; transform: none; }
.heatmap-inner { max-width: 1500px; margin: 0 auto; }
.heatmap-header { max-width: 720px; margin-bottom: 36px; }
.section-label { font-family: system-ui,sans-serif; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #0a9b8a; margin-bottom: 14px; }
.section-heading { font-family: Georgia,serif; font-size: clamp(32px, 4vw, 48px); font-weight: 700; line-height: 1.06; color: #0f1e12; margin-bottom: 14px; }
.section-heading em { color: #0a9b8a; font-style: italic; }
.section-sub { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.65; }

.heatmap-wrap { overflow-x: auto; padding-bottom: 6px; }
.heat-grid { display: grid; grid-template-columns: 56px repeat(13, 1fr); gap: 5px; min-width: 720px; align-items: center; }
.axis-row { margin-bottom: 6px; }
.day-spacer { width: 56px; }
.hour-label { font-family: system-ui,sans-serif; font-size: 11px; font-weight: 700; color: #6a8e6e; text-align: center; }
.day-row { margin-bottom: 5px; }
.day-label { font-family: system-ui,sans-serif; font-size: 13px; font-weight: 800; color: #0f1e12; text-align: right; padding-right: 10px; }
.heat-cell { height: 36px; border: none; border-radius: 6px; cursor: pointer; padding: 0; position: relative; display: flex; align-items: center; justify-content: center; transition: transform 0.12s ease, box-shadow 0.12s; box-shadow: inset 0 1px 0 rgba(255,255,255,0.18), inset 0 -1px 0 rgba(0,0,0,0.06); }
.heat-cell:hover { transform: scale(1.1); z-index: 2; box-shadow: 0 4px 12px rgba(0,0,0,0.22); }
.heat-cell:focus-visible { outline: 3px solid #0a9b8a; outline-offset: 2px; }
.cell-selected { outline: 3px solid white; outline-offset: -3px; transform: scale(1.1); z-index: 3; box-shadow: 0 4px 16px rgba(0,0,0,0.28); }
.cell-best { outline: 2.5px solid white; outline-offset: -2px; z-index: 4; }
.best-star { display: inline-flex; }

.legend-row { display: grid; grid-template-columns: 56px 1fr; align-items: center; margin-top: 14px; }
.legend-content { display: flex; align-items: center; gap: 12px; }
.legend-label { font-family: system-ui,sans-serif; font-size: 11px; font-weight: 700; color: #6a8e6e; }
.legend-bar { flex: 1; height: 10px; border-radius: 999px; background: linear-gradient(90deg, rgb(10,110,98) 0%, rgb(86,154,102) 25%, rgb(212,168,84) 50%, rgb(196,110,76) 75%, rgb(156,60,50) 100%); }

.cell-detail { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; margin-top: 24px; padding: 16px 20px; background: white; border: 2px solid #0a9b8a; border-radius: 14px; box-shadow: 0 12px 28px rgba(10,155,138,0.18); animation: fade-in 0.18s ease; }
@keyframes fade-in { from { opacity: 0; transform: translateY(-6px); } to { opacity: 1; transform: none; } }
.cd-icon { width: 38px; height: 38px; border-radius: 10px; background: #d6f4e7; color: #1d7169; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.cd-text { display: flex; flex-direction: column; gap: 4px; flex: 1; min-width: 180px; }
.cd-when { font-family: Georgia,serif; font-size: 16px; font-weight: 700; color: #0f1e12; }
.cd-meta { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.cd-count { font-family: system-ui,sans-serif; font-size: 13px; color: #6a8e6e; font-weight: 600; }
.crowd-badge { padding: 4px 12px; border-radius: 999px; font-family: system-ui,sans-serif; font-size: 12px; font-weight: 700; }
.crowd-low      { background: #d6f4e7; color: #1d7169; }
.crowd-moderate { background: #fff3c2; color: #b88a00; }
.crowd-high     { background: #ffded5; color: #c44a2c; }
.cd-plan-btn { display: inline-flex; align-items: center; gap: 7px; padding: 9px 16px; background: linear-gradient(135deg, #0a9b8a, #056b5e); color: white; border-radius: 10px; font-family: system-ui,sans-serif; font-size: 13px; font-weight: 700; text-decoration: none; flex-shrink: 0; }
.cd-plan-btn:hover { background: #056b5e; }
.cd-close { width: 28px; height: 28px; border-radius: 50%; border: 1px solid rgba(29,113,105,0.2); background: white; color: #6a8e6e; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.15s; flex-shrink: 0; }
.cd-close:hover { color: #c44a2c; border-color: #c44a2c; }
.data-note { margin-top: 18px; font-family: system-ui,sans-serif; font-size: 12px; color: #8aaa8e; font-style: italic; }

/* ═══ CREAM BAND — full width ═══ */
.cream-band { background: linear-gradient(180deg, #faf8f0 0%, #f4f8e8 100%); padding: 80px 52px; border-bottom: 1px solid rgba(29,113,105,0.1); opacity: 0; transform: translateY(40px); transition: all 0.9s cubic-bezier(0.22,1,0.36,1); }
.cream-band.in-view { opacity: 1; transform: none; }
.cream-inner { width: 100%; max-width: none; }
.card-label { font-family: system-ui,sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; color: #0a9b8a; margin-bottom: 14px; }

/* Quietest day — full-width horizontal card */
.quietest-card-wrap { margin-bottom: 32px; }
.quietest-card {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: 40px;
  background: linear-gradient(135deg, #f0faf0 0%, white 60%);
  border: 1.5px solid rgba(10,155,138,0.25);
  border-radius: 24px;
  padding: 32px 40px;
  box-shadow: 0 16px 40px rgba(10,155,138,0.12);
}
.qd-content { min-width: 0; }
.qd-day { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; line-height: 1; margin-bottom: 8px; }
.qd-best { font-family: system-ui,sans-serif; color: #4a6a4e; font-weight: 600; font-size: 15px; }
.qd-aside { display: flex; flex-direction: column; align-items: flex-end; gap: 14px; flex-shrink: 0; }
.qd-stats { display: flex; align-items: center; gap: 12px; }
.qd-count { font-family: system-ui,sans-serif; font-size: 13px; color: #6a8e6e; font-weight: 600; }
.qd-cta { display: inline-flex; align-items: center; gap: 8px; padding: 12px 22px; background: #0a9b8a; color: white; border-radius: 12px; font-family: system-ui,sans-serif; font-size: 14px; font-weight: 700; text-decoration: none; transition: all 0.25s; }
.qd-cta:hover { background: #056b5e; transform: translateY(-1px); }

/* Full-width 3-card stats strip */
.stats-strip {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 22px;
}
.stat-card-big {
  display: flex; flex-direction: column; align-items: flex-start; gap: 12px;
  padding: 36px 32px;
  background: white;
  border: 1px solid rgba(29,113,105,0.14);
  border-radius: 22px;
  box-shadow: 0 8px 24px rgba(10,155,138,0.06);
  transition: transform 0.3s, box-shadow 0.3s;
}
.stat-card-big:hover { transform: translateY(-3px); box-shadow: 0 16px 36px rgba(10,155,138,0.14); }
.stat-icon-big {
  width: 64px; height: 64px; border-radius: 18px;
  display: flex; align-items: center; justify-content: center;
  position: relative;
}
.stat-icon-big::before { content: ''; position: absolute; inset: -4px; border: 1.5px solid currentColor; border-radius: 18px; opacity: 0.18; }
.stat-icon-big.mint   { background: #d6f4e7; color: #1d7169; }
.stat-icon-big.purple { background: #e6dcff; color: #5b3fb6; }
.stat-icon-big.yellow { background: #fff3c2; color: #b88a00; }
.stat-num-big { font-family: Georgia,serif; font-weight: 700; color: #0a9b8a; line-height: 1; letter-spacing: -0.02em; }
.stat-label-big {
  font-family: system-ui,sans-serif; font-size: 13px; font-weight: 800;
  color: #4a6a4e; letter-spacing: 0.08em; text-transform: uppercase;
}

/* ═══ FULL-WIDTH SPACES BAND ═══ */
.spaces-band {
  background: white;
  padding: 90px 52px;
  border-bottom: 1px solid rgba(29,113,105,0.1);
  opacity: 0; transform: translateY(40px);
  transition: all 0.9s cubic-bezier(0.22,1,0.36,1);
}
.spaces-band.in-view { opacity: 1; transform: none; }
.spaces-inner { width: 100%; max-width: none; }

.spaces-band-header { margin-bottom: 36px; }

/* Title + animation 2-col grid */
.title-with-animation {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 40px;
  align-items: center;
  margin-bottom: 36px;
}
.spaces-band-title { max-width: 760px; }

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

.park-sun { animation: sun-rays 16s linear infinite; transform-box: fill-box; }
@keyframes sun-rays { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.park-cloud.c1 { animation: cloud-drift-1 24s ease-in-out infinite alternate; }
.park-cloud.c2 { animation: cloud-drift-2 30s ease-in-out infinite alternate-reverse; }
@keyframes cloud-drift-1 { 0% { transform: translateX(-20px); } 100% { transform: translateX(40px); } }
@keyframes cloud-drift-2 { 0% { transform: translateX(0); } 100% { transform: translateX(-30px); } }

.park-bird.b1 { animation: bird-fly-1 14s linear infinite; }
.park-bird.b2 { animation: bird-fly-2 18s linear infinite; }
@keyframes bird-fly-1 { 0% { transform: translate(-30px, 80px); } 100% { transform: translate(360px, 50px); } }
@keyframes bird-fly-2 { 0% { transform: translate(360px, 100px); } 100% { transform: translate(-30px, 70px); } }

.park-tree.t-left { animation: tree-sway 4.5s ease-in-out infinite alternate; }
.park-tree.t-right { animation: tree-sway-2 5.5s ease-in-out infinite alternate-reverse; }
@keyframes tree-sway { 0% { transform: rotate(-1.5deg); } 100% { transform: rotate(1.5deg); } }
@keyframes tree-sway-2 { 0% { transform: rotate(1deg); } 100% { transform: rotate(-1deg); } }

.park-person { animation: person-bounce 1.6s ease-in-out infinite; }
@keyframes person-bounce { 0%, 100% { transform: translate(190px, 215px); } 50% { transform: translate(190px, 213px); } }

.arm-wave { animation: arm-wave 2.4s ease-in-out infinite; transform-box: fill-box; }
@keyframes arm-wave { 0%, 100% { transform: rotate(0deg); } 50% { transform: rotate(15deg); } }

.park-butterfly { animation: butterfly-fly 12s ease-in-out infinite; transform-box: fill-box; }
@keyframes butterfly-fly {
  0%   { transform: translate(80px, 130px); }
  25%  { transform: translate(140px, 100px); }
  50%  { transform: translate(200px, 140px); }
  75%  { transform: translate(150px, 120px); }
  100% { transform: translate(80px, 130px); }
}
.bf-wings { animation: bf-flap 0.32s ease-in-out infinite alternate; transform-box: fill-box; transform-origin: center; }
@keyframes bf-flap { 0% { transform: scaleX(1); } 100% { transform: scaleX(0.45); } }

/* Centered sort controls */
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
.control-label {
  font-family: system-ui,sans-serif; font-size: 11px; font-weight: 800;
  letter-spacing: 0.08em; text-transform: uppercase; color: #6a8e6e;
}
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

.results-summary {
  text-align: center;
  font-family: system-ui,sans-serif; font-size: 13px; color: #6a8e6e; font-weight: 500;
  margin-top: 8px;
}
.results-summary strong { color: #0a9b8a; font-weight: 800; }
.results-summary em { color: #1a2e1e; font-style: italic; font-weight: 700; }

.mini-loading { display: flex; align-items: center; justify-content: center; gap: 10px; color: #6a8e6e; font-family: system-ui,sans-serif; font-weight: 600; padding: 30px 0; }
.mini-spin { width: 18px; height: 18px; border-radius: 50%; border: 2px solid rgba(10,155,138,0.2); border-top-color: #0a9b8a; animation: spin 0.7s linear infinite; }

.spaces-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.space-card {
  display: flex; flex-direction: column; gap: 16px;
  padding: 24px 22px;
  background: white;
  border: 1px solid rgba(29,113,105,0.12);
  border-radius: 18px;
  transition: transform 0.25s, box-shadow 0.25s, border-color 0.25s;
}
.space-card:hover { transform: translateY(-3px); box-shadow: 0 16px 36px rgba(10,155,138,0.12); border-color: rgba(10,155,138,0.3); }

.space-card-head { display: flex; align-items: flex-start; gap: 14px; }
.space-icon {
  width: 46px; height: 46px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.space-icon.green { background: #d6f4e7; color: #1d7169; }
.space-icon.leisure { background: #fff3c2; color: #8a6000; }
.space-icon.neutral { background: #f0f0f8; color: #4a6a4e; }

.space-titles { flex: 1; min-width: 0; }
.space-name { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; line-height: 1.2; margin-bottom: 4px; }
.space-meta-line { display: inline-flex; align-items: center; gap: 6px; flex-wrap: wrap; font-family: system-ui,sans-serif; font-size: 13px; color: #6a8e6e; font-weight: 600; }
.meta-distance { display: inline-flex; align-items: center; gap: 5px; }
.meta-distance svg { color: #0a9b8a; }
.meta-sep { color: #c5d6c7; }

.space-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.toilet-pill {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 3px 10px; border-radius: 999px;
  font-family: system-ui,sans-serif; font-size: 11px; font-weight: 800;
  letter-spacing: 0.04em; text-transform: uppercase;
  white-space: nowrap;
}
.toilet-pill.yes { background: #d6f4e7; color: #0a6e62; }
.toilet-pill.no  { background: #f5e4dc; color: #a04a1a; }
.info-tag.access { background: #e8e8ff; color: #2a2ab0; padding: 3px 10px; border-radius: 999px; font-family: system-ui,sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; }

.metric-bars { display: flex; flex-direction: column; gap: 8px; }
.metric-row {
  display: grid;
  grid-template-columns: 86px 1fr 38px;
  gap: 10px;
  align-items: center;
}
.metric-label { font-family: system-ui,sans-serif; font-size: 11px; font-weight: 700; color: #6a8e6e; letter-spacing: 0.04em; text-transform: uppercase; }
.metric-track { height: 6px; background: #eaf4ea; border-radius: 999px; overflow: hidden; }
.metric-fill { height: 100%; border-radius: 999px; transition: width 0.6s cubic-bezier(0.22,1,0.36,1); }
.metric-fill.comfort.high { background: linear-gradient(90deg, #0a9b8a, #1d7169); }
.metric-fill.comfort.mid  { background: linear-gradient(90deg, #d4a854, #b88a00); }
.metric-fill.comfort.low  { background: #c44a2c; }
.metric-fill.walk { background: linear-gradient(90deg, #5b3fb6, #8a6dd1); }
.metric-num { font-family: Georgia,serif; font-size: 14px; font-weight: 700; color: #0f1e12; text-align: right; }

.managed-by-line {
  display: inline-flex; align-items: center; gap: 6px;
  font-family: system-ui,sans-serif; font-size: 12px; color: #8aaa8e; font-weight: 500;
  padding-top: 10px; border-top: 1px solid rgba(29,113,105,0.08);
}
.managed-by-line svg { color: #0a9b8a; }

/* Get directions button at bottom of each card */
.directions-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  width: 100%;
  padding: 12px 18px;
  background: linear-gradient(135deg, #0a9b8a, #056b5e);
  color: white;
  border: none; border-radius: 12px;
  font-family: system-ui,sans-serif; font-size: 14px; font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 8px 20px rgba(10,155,138,0.28);
  margin-top: auto;
}
.directions-btn:hover { transform: translateY(-2px); box-shadow: 0 14px 28px rgba(10,155,138,0.4); }
.directions-btn .dir-arrow { transition: transform 0.25s; }
.directions-btn:hover .dir-arrow { transform: translateX(3px); }

.filter-empty {
  display: flex; flex-direction: column; align-items: center; gap: 12px;
  padding: 60px 40px; text-align: center;
  background: #f6faf3; border: 1px dashed rgba(29,113,105,0.25);
  border-radius: 18px; color: #6a8e6e;
}
.filter-empty svg { color: #0a9b8a; }
.filter-empty p { font-family: system-ui,sans-serif; }

.show-more-wrap { display: flex; justify-content: center; margin-top: 24px; }
.show-more-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  padding: 14px 28px;
  background: white; border: 1.5px dashed rgba(10,155,138,0.4); color: #0a9b8a;
  border-radius: 14px; cursor: pointer;
  font-family: system-ui,sans-serif; font-size: 14px; font-weight: 700;
  transition: all 0.2s;
}
.show-more-btn:hover { background: #0a9b8a; color: white; border-color: #0a9b8a; border-style: solid; }
.show-more-btn svg { transition: transform 0.25s; }

/* Bottom nav */
.bottom-nav-band { padding: 50px 52px 80px; }
.bottom-nav-inner { max-width: 1100px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; }
.bnav-btn { display: inline-flex; align-items: center; justify-content: center; gap: 10px; padding: 18px 24px; border-radius: 14px; background: white; border: 1.5px solid rgba(29,113,105,0.2); color: #1a2e1e; font-family: system-ui,sans-serif; font-weight: 700; text-decoration: none; transition: all 0.25s; }
.bnav-btn:hover { border-color: #0a9b8a; color: #0a9b8a; }
.bnav-btn.primary { background: linear-gradient(135deg, #0a9b8a, #056b5e); color: white; border-color: transparent; box-shadow: 0 12px 28px rgba(10,155,138,0.3); }
.bnav-btn.primary:hover { color: white; transform: translateY(-2px); box-shadow: 0 16px 36px rgba(10,155,138,0.38); }

@media (max-width: 1300px) {
  .title-with-animation { grid-template-columns: 1fr 280px; }
}
@media (max-width: 1200px) {
  .spaces-grid { grid-template-columns: repeat(2, 1fr); }
  .stats-strip { grid-template-columns: repeat(3, 1fr); }
  .quietest-card { grid-template-columns: 1fr; gap: 20px; }
  .qd-aside { align-items: flex-start; }
}
@media (max-width: 1100px) {
  .best-window-callout { right: 20px; left: 20px; bottom: -50px; }
  .title-with-animation { grid-template-columns: 1fr; }
  .park-animation { justify-self: center; max-width: 320px; }
}
@media (max-width: 980px) {
  .hero { padding: 280px 20px 140px; }
  .heatmap-band, .cream-band, .spaces-band { padding: 60px 20px; }
  .empty-band, .loading-band { padding: 80px 20px 60px; }
  .stats-strip { grid-template-columns: 1fr; }
  .stat-card-big { padding: 28px 24px; align-items: center; text-align: center; }
  .spaces-grid { grid-template-columns: 1fr; }
  .sort-controls-wrap { width: 100%; padding: 14px 16px; }
  .control-group { flex-direction: column; align-items: flex-start; gap: 10px; width: 100%; }
  .pill-row { width: 100%; }
  .filter-pill { flex: 1; justify-content: center; }
  .metric-row { grid-template-columns: 70px 1fr 30px; }
  .quietest-card { padding: 24px 20px; }
  .bottom-nav-band { padding: 40px 20px 70px; }
  .bottom-nav-inner { grid-template-columns: 1fr; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
</style>

<style>
.heat-tooltip {
  position: fixed;
  transform: translate(-50%, -100%);
  background: white;
  border: 1px solid rgba(29,113,105,0.18);
  border-radius: 12px;
  padding: 10px 14px;
  box-shadow: 0 14px 36px rgba(0,0,0,0.14), 0 4px 10px rgba(0,0,0,0.06);
  pointer-events: none;
  z-index: 9999;
  white-space: nowrap;
  font-family: system-ui, sans-serif;
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 160px;
}
.heat-tooltip .tip-when { font-family: Georgia, serif; font-weight: 700; font-size: 14px; color: #0f1e12; }
.heat-tooltip .tip-meta { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.heat-tooltip .tip-badge { padding: 3px 10px; }
.heat-tooltip .tip-count { font-size: 12px; color: #6a8e6e; font-weight: 600; }
.heat-tooltip .tip-arrow {
  position: absolute; bottom: -6px; left: 50%;
  transform: translateX(-50%) rotate(45deg);
  width: 12px; height: 12px;
  background: white;
  border-right: 1px solid rgba(29,113,105,0.18);
  border-bottom: 1px solid rgba(29,113,105,0.18);
}
.tip-fade-enter-active, .tip-fade-leave-active { transition: opacity 0.12s ease, transform 0.12s ease; }
.tip-fade-enter-from, .tip-fade-leave-to { opacity: 0; transform: translate(-50%, -100%) translateY(4px); }
</style>