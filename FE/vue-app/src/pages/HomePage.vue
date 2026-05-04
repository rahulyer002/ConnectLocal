<template>
  <div class="page" @mousemove="handleMouse">

    <div class="noise" aria-hidden="true"></div>
    <div class="orb orb-1" aria-hidden="true"></div>
    <div class="orb orb-2" aria-hidden="true"></div>

    <nav class="nav" :class="{ scrolled: scrollY > 60 }">
      <div class="nav-brand">
        <div class="nav-logo">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/>
            <circle cx="12" cy="10" r="2.5"/>
          </svg>
        </div>
        <span class="nav-wordmark"><em>Connect</em>Local</span>
      </div>
      <div class="nav-links">
        <RouterLink to="/home">Home</RouterLink>
        <RouterLink to="/discover">Events</RouterLink>
        <span class="nav-link-coming">Places</span>
        <RouterLink to="/about">About</RouterLink>
        <RouterLink to="/resources">Resources</RouterLink>
      </div>
      <RouterLink to="/checkin" class="nav-cta">
        Start Check-in
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M5 12h14M13 5l7 7-7 7"/>
        </svg>
      </RouterLink>
    </nav>

    <div class="a11y-bar" role="region" aria-label="Accessibility options">
      <div class="a11y-inner">
        <div class="text-size-control" role="group" aria-label="Adjust text size">
          <span class="a-small" aria-hidden="true">A</span>
          <input
            type="range"
            class="text-slider"
            min="90"
            max="140"
            step="5"
            v-model.number="textScale"
            aria-label="Text size"
            aria-valuemin="90"
            aria-valuemax="140"
            :aria-valuenow="textScale"
            :aria-valuetext="`Text size ${textScale}%`"
          />
          <span class="a-large" aria-hidden="true">A</span>
          <span class="scale-pct" aria-hidden="true">{{ textScale }}%</span>
        </div>
      </div>
    </div>

    <section class="hero">
      <div
        class="hero-bg-text"
        :style="{ transform: `translateY(${scrollY * 0.18}px)` }"
        aria-hidden="true"
      >CONNECT</div>

      <div class="hero-tag tag-1" :style="{ transform: `translate(${mouse.x * -0.018}px, ${mouse.y * -0.014}px)` }">
        <span class="tag-dot"></span> Real connections
      </div>
      <div class="hero-tag tag-2" :style="{ transform: `translate(${mouse.x * 0.022}px, ${mouse.y * 0.016}px)` }">
        <span class="tag-dot"></span> Local places
      </div>
      <div class="hero-tag tag-3" :style="{ transform: `translate(${mouse.x * -0.012}px, ${mouse.y * 0.02}px)` }">
        <span class="tag-dot"></span> Melbourne
      </div>

      <div class="hero-content">
        <div class="hero-eyebrow" data-reveal>A community of warmth</div>
        <h1 class="hero-headline" data-reveal>
          <span class="line">You're not</span>
          <span class="line line-accent">alone</span>
          <span class="line">in this.</span>
        </h1>
        <div class="hero-sub" data-reveal>
          <p :style="{ fontSize: scaledPx(18) }">People of all ages experience challenges<br>with social connection and wellbeing.</p>
          <p :style="{ fontSize: scaledPx(18) }">Small steps can help build a more connected life.</p>
        </div>
        <RouterLink to="/discover" class="hero-cta" data-reveal @mousemove="magnetMove" @mouseleave="magnetLeave">
          <span>Explore activities near you</span>
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M5 12h14M13 5l7 7-7 7"/>
          </svg>
        </RouterLink>
      </div>

      <div class="hero-scene" :style="{ transform: `translateY(${scrollY * 0.08}px)` }">
        <svg viewBox="0 0 520 640" class="scene-svg" aria-hidden="true">
          <defs>
            <radialGradient id="sg" cx="50%" cy="60%" r="60%">
              <stop offset="0%" stop-color="#c8edc8"/>
              <stop offset="100%" stop-color="#e8f5e2"/>
            </radialGradient>
            <linearGradient id="hg" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#a8d8a8"/>
              <stop offset="100%" stop-color="#5cb471"/>
            </linearGradient>
            <linearGradient id="hg2" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#6abf80"/>
              <stop offset="100%" stop-color="#3e9c5a"/>
            </linearGradient>
            <linearGradient id="hg3" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#3e9c5a"/>
              <stop offset="100%" stop-color="#2a7040"/>
            </linearGradient>
            <filter id="blur-sm"><feGaussianBlur stdDeviation="1.5"/></filter>
            <filter id="blur-md"><feGaussianBlur stdDeviation="4"/></filter>
          </defs>

          <rect width="520" height="640" fill="url(#sg)"/>
          <circle cx="400" cy="110" r="90" fill="#ffe9a1" opacity="0.28" filter="url(#blur-md)"/>
          <circle cx="400" cy="110" r="50" fill="#ffd56b" opacity="0.55" filter="url(#blur-sm)"/>
          <g class="sun-rays" style="transform-origin:400px 110px">
            <g v-for="i in 10" :key="i" :transform="`rotate(${i*36} 400 110)`">
              <line x1="400" y1="52" x2="400" y2="42" stroke="#ffcc44" stroke-width="2.5" stroke-linecap="round" opacity="0.7"/>
            </g>
          </g>
          <circle cx="400" cy="110" r="22" fill="#ffd56b"/>

          <g class="cloud c1" opacity="0.9" fill="white">
            <ellipse cx="80" cy="130" rx="48" ry="16"/>
            <ellipse cx="60" cy="122" rx="24" ry="16"/>
            <ellipse cx="104" cy="120" rx="28" ry="16"/>
          </g>
          <g class="cloud c2" opacity="0.85" fill="white">
            <ellipse cx="260" cy="80" rx="36" ry="11"/>
            <ellipse cx="244" cy="74" rx="18" ry="11"/>
            <ellipse cx="278" cy="74" rx="22" ry="11"/>
          </g>

          <g class="bird b1" fill="none" stroke="#2d5a3d" stroke-width="2.2" stroke-linecap="round">
            <path d="M0 0 q5-6 10 0 q5-6 10 0"/>
          </g>
          <g class="bird b2" fill="none" stroke="#2d5a3d" stroke-width="1.8" stroke-linecap="round">
            <path d="M0 0 q4-5 8 0 q4-5 8 0"/>
          </g>

          <g opacity="0.35" fill="#6a9e78">
            <rect x="18" y="330" width="22" height="56"/>
            <rect x="42" y="314" width="18" height="72"/>
            <rect x="62" y="342" width="26" height="44"/>
            <rect x="90" y="322" width="16" height="64"/>
            <rect x="108" y="348" width="22" height="38"/>
            <rect x="132" y="335" width="14" height="51"/>
            <rect x="47" y="328" width="2.5" height="2.5" fill="#fffde0" opacity="0.8"/>
            <rect x="53" y="328" width="2.5" height="2.5" fill="#fffde0" opacity="0.8"/>
            <rect x="47" y="342" width="2.5" height="2.5" fill="#fffde0" opacity="0.8"/>
            <rect x="95" y="334" width="2.5" height="2.5" fill="#fffde0" opacity="0.8"/>
          </g>

          <g>
            <rect x="370" y="310" width="80" height="74" fill="#d4b896"/>
            <polygon points="365,310 455,310 410,282" fill="#8b5e30"/>
            <rect x="365" y="310" width="80" height="5" fill="#6b4422"/>
            <rect x="372" y="330" width="70" height="7" fill="#1d7169"/>
            <polygon points="372,337 380,347 388,337" fill="#1d7169"/>
            <polygon points="388,337 396,347 404,337" fill="#1d7169"/>
            <polygon points="404,337 412,347 420,337" fill="#1d7169"/>
            <polygon points="420,337 428,347 436,337" fill="#1d7169"/>
            <rect x="398" y="352" width="16" height="32" rx="2" fill="#4a2e10"/>
            <rect x="374" y="352" width="20" height="18" fill="#fffde0"/>
            <rect x="374" y="352" width="20" height="18" fill="none" stroke="#6b4422" stroke-width="1.2"/>
            <line x1="384" y1="352" x2="384" y2="370" stroke="#6b4422" stroke-width="0.8"/>
            <rect x="420" y="352" width="20" height="18" fill="#fffde0"/>
            <rect x="420" y="352" width="20" height="18" fill="none" stroke="#6b4422" stroke-width="1.2"/>
            <line x1="430" y1="352" x2="430" y2="370" stroke="#6b4422" stroke-width="0.8"/>
            <rect x="428" y="288" width="5" height="14" fill="#6b4422"/>
            <circle cx="430" cy="283" r="3" fill="white" opacity="0.55" class="smoke s1"/>
            <circle cx="432" cy="275" r="2.5" fill="white" opacity="0.45" class="smoke s2"/>
            <circle cx="430" cy="267" r="2" fill="white" opacity="0.35" class="smoke s3"/>
          </g>

          <path d="M0 390 Q130 330 260 368 T520 355 L520 640 L0 640Z" fill="url(#hg)"/>
          <path d="M0 430 Q180 380 360 415 T520 405 L520 640 L0 640Z" fill="url(#hg2)"/>
          <path d="M0 472 Q130 448 260 462 T520 456 L520 640 L0 640Z" fill="url(#hg3)"/>

          <path d="M20 638 Q200 595 260 588 Q320 595 500 638" stroke="#d4b87a" stroke-width="42" fill="none" stroke-linecap="round" opacity="0.9"/>
          <path d="M20 638 Q200 595 260 588 Q320 595 500 638" stroke="#e4cfa0" stroke-width="32" fill="none" stroke-linecap="round"/>

          <g class="tree t1" style="transform-origin:72px 408px">
            <rect x="69" y="385" width="6" height="44" fill="#4a2e10"/>
            <circle cx="72" cy="381" r="24" fill="#2a7040"/>
            <circle cx="59" cy="377" r="15" fill="#3e9c5a"/>
            <circle cx="85" cy="379" r="15" fill="#4fae6b"/>
            <circle cx="72" cy="367" r="13" fill="#5cb471"/>
          </g>
          <g class="tree t2" style="transform-origin:468px 420px">
            <rect x="465" y="400" width="5" height="36" fill="#4a2e10"/>
            <circle cx="468" cy="396" r="19" fill="#2a7040"/>
            <circle cx="459" cy="392" r="12" fill="#3e9c5a"/>
            <circle cx="477" cy="394" r="12" fill="#4fae6b"/>
          </g>

          <g transform="translate(158 478)">
            <rect x="-1.5" y="0" width="3" height="52" fill="#222"/>
            <rect x="-4" y="50" width="8" height="3" fill="#222"/>
            <path d="M0 0 q0-9 9-9" stroke="#222" stroke-width="2.5" fill="none"/>
            <rect x="7" y="-16" width="6" height="9" rx="1" fill="#222"/>
            <circle cx="10" cy="-10" r="3.5" fill="#fffde0" class="lamp"/>
          </g>

          <g transform="translate(390 463)">
            <rect x="-34" y="0" width="68" height="5" fill="#6b4226" rx="1.5"/>
            <rect x="-34" y="-11" width="68" height="5" fill="#6b4226" rx="1.5"/>
            <rect x="-30" y="5" width="4" height="15" fill="#6b4226"/>
            <rect x="26" y="5" width="4" height="15" fill="#6b4226"/>
          </g>

          <g opacity="0.9">
            <g transform="translate(46 534)"><circle r="2.5" fill="#ff8b6b"/><circle r="1" fill="#ffd56b"/></g>
            <g transform="translate(66 548)"><circle r="2" fill="#ffb199"/><circle r="0.8" fill="#ffd56b"/></g>
            <g transform="translate(188 552)"><circle r="2.5" fill="#fff"/><circle r="1" fill="#ffd56b"/></g>
            <g transform="translate(214 546)"><circle r="2" fill="#ffd56b"/><circle r="0.7" fill="#fff"/></g>
            <g transform="translate(330 548)"><circle r="2.2" fill="#e6dcff"/><circle r="0.8" fill="#ffd56b"/></g>
            <g transform="translate(360 554)"><circle r="2" fill="#fff"/><circle r="0.7" fill="#ffd56b"/></g>
            <g transform="translate(490 546)"><circle r="2.2" fill="#ff8b6b"/><circle r="0.8" fill="#ffd56b"/></g>
          </g>

          <g class="butterfly">
            <g class="bf-wings">
              <ellipse cx="-3" cy="-1" rx="4" ry="5.5" fill="#ff8b6b" opacity="0.85"/>
              <ellipse cx="3" cy="-1" rx="4" ry="5.5" fill="#ffb199" opacity="0.85"/>
              <ellipse cx="-3" cy="3.5" rx="3" ry="4" fill="#ff8b6b" opacity="0.85"/>
              <ellipse cx="3" cy="3.5" rx="3" ry="4" fill="#ffb199" opacity="0.85"/>
            </g>
            <line x1="0" y1="-5" x2="0" y2="5" stroke="#333" stroke-width="1.5"/>
          </g>

          <g class="person p1">
            <ellipse cx="0" cy="33" rx="13" ry="2.5" fill="#000" opacity="0.12"/>
            <rect x="-13" y="-23" width="6" height="22" rx="3" fill="#6b4226"/>
            <g class="leg pl1-lb"><rect x="-1.5" y="0" width="5" height="25" rx="2.5" fill="#223344"/><ellipse cx="1" cy="27" rx="5" ry="2" fill="#111"/></g>
            <g class="arm pl1-ab" style="transform-origin:-9px -16px"><rect x="-11" y="-16" width="4" height="15" rx="2" fill="#0e6055"/><circle cx="-9" cy="0" r="2.5" fill="#f0c8a0"/></g>
            <path d="M-10-23 Q-11-10 -9 4 L9 4 Q11-10 10-23 Q5-26 0-26 Q-5-26 -10-23Z" fill="#1d7169"/>
            <line x1="-5" y1="-24" x2="-7" y2="0" stroke="#4a2e10" stroke-width="1.8"/>
            <line x1="5" y1="-24" x2="7" y2="0" stroke="#4a2e10" stroke-width="1.8"/>
            <rect x="-2.5" y="-27" width="5" height="5" fill="#f0c8a0"/>
            <circle cx="0" cy="-33" r="9.5" fill="#f0c8a0"/>
            <path d="M-9.5-34 Q-9-44 0-44 Q9-44 9.5-34 Q7-39 4-37 Q0-40 -4-37 Q-7-39 -9.5-34Z" fill="#1a0e08"/>
            <circle cx="-3" cy="-32" r="1" fill="#111"/>
            <circle cx="3" cy="-32" r="1" fill="#111"/>
            <path d="M-2-28 Q0-26.5 2-28" stroke="#333" stroke-width="0.9" fill="none" stroke-linecap="round"/>
            <g class="leg pl1-lf"><rect x="-3.5" y="0" width="5" height="25" rx="2.5" fill="#2a3a50"/><ellipse cx="-1" cy="27" rx="5" ry="2" fill="#1a1a1a"/></g>
            <g class="wave-arm" style="transform-origin:9px -16px"><rect x="7" y="-16" width="4" height="15" rx="2" fill="#1d7169"/><circle cx="9" cy="-1" r="2.5" fill="#f0c8a0"/></g>
            <g class="speech sp1">
              <rect x="-36" y="-56" width="24" height="14" rx="7" fill="white" stroke="#cfe6d4" stroke-width="1.2"/>
              <path d="M-18-43 L-15-38 L-12-43Z" fill="white" stroke="#cfe6d4" stroke-width="1.2" stroke-linejoin="round"/>
              <line x1="-14" y1="-43" x2="-12" y2="-43" stroke="white" stroke-width="1.5"/>
              <circle cx="-30" cy="-50" r="1.5" fill="#1d7169" class="dot d1"/>
              <circle cx="-24" cy="-50" r="1.5" fill="#1d7169" class="dot d2"/>
              <circle cx="-18" cy="-50" r="1.5" fill="#1d7169" class="dot d3"/>
            </g>
          </g>

          <g class="person p2">
            <ellipse cx="0" cy="33" rx="13" ry="2.5" fill="#000" opacity="0.12"/>
            <g class="leg pl2-lb"><rect x="-1.5" y="0" width="5" height="25" rx="2.5" fill="#3a4a2e"/><ellipse cx="1" cy="27" rx="5" ry="2" fill="#eee"/></g>
            <g class="arm pl2-ab" style="transform-origin:9px -16px">
              <rect x="7" y="-16" width="4" height="15" rx="2" fill="#e07060"/>
              <circle cx="9" cy="0" r="2.5" fill="#f0c8a0"/>
              <path d="M9 0 Q15 9 24 18" stroke="#444" stroke-width="1.3" fill="none"/>
            </g>
            <path d="M-10-23 Q-11-10 -9 4 L9 4 Q11-10 10-23 Q5-26 0-26 Q-5-26 -10-23Z" fill="#e87060"/>
            <line x1="0" y1="-23" x2="0" y2="4" stroke="#b84d3c" stroke-width="0.9"/>
            <path d="M-6-23 Q0-20 6-23" stroke="#fff" stroke-width="2.2" fill="none"/>
            <rect x="-2.5" y="-27" width="5" height="5" fill="#f0c8a0"/>
            <circle cx="0" cy="-33" r="9.5" fill="#f0c8a0"/>
            <path d="M-9.5-32 Q-9-43 0-43 Q9-43 9.5-32 L9.5-28 Q9.5-37 0-37 Q-9.5-37 -9.5-28Z" fill="#5a3010"/>
            <circle cx="-8" cy="-42" r="3.5" fill="#5a3010"/>
            <circle cx="-7" cy="-30" r="0.7" fill="#ffd56b"/>
            <path d="M-4-32 Q-3-33 -2-32" stroke="#111" stroke-width="1" fill="none" stroke-linecap="round"/>
            <path d="M2-32 Q3-33 4-32" stroke="#111" stroke-width="1" fill="none" stroke-linecap="round"/>
            <path d="M-3-28 Q0-25.5 3-28" stroke="#333" stroke-width="1" fill="none" stroke-linecap="round"/>
            <circle cx="-5.5" cy="-29" r="1.5" fill="#ffb199" opacity="0.45"/>
            <circle cx="5.5" cy="-29" r="1.5" fill="#ffb199" opacity="0.45"/>
            <g class="leg pl2-lf"><rect x="-3.5" y="0" width="5" height="25" rx="2.5" fill="#4a5e38"/><ellipse cx="-1" cy="27" rx="5" ry="2" fill="#eee"/></g>
            <g class="arm pl2-af" style="transform-origin:-9px -16px">
              <rect x="-11" y="-16" width="4" height="13" rx="2" fill="#e87060"/>
              <circle cx="-9" cy="-3" r="2.5" fill="#f0c8a0"/>
              <rect x="-13" y="-11" width="9" height="9" rx="1.2" fill="white" stroke="#1d7169" stroke-width="1.1"/>
              <rect x="-13" y="-13" width="9" height="3" fill="#1d7169"/>
              <g class="steam">
                <path d="M-11-15 q-1-3 0-6" stroke="#b8d6c0" stroke-width="1.1" fill="none" stroke-linecap="round"/>
                <path d="M-9-15 q1-3 0-6" stroke="#b8d6c0" stroke-width="1.1" fill="none" stroke-linecap="round"/>
              </g>
            </g>
            <g class="speech sp2">
              <rect x="12" y="-56" width="24" height="14" rx="7" fill="white" stroke="#cfe6d4" stroke-width="1.2"/>
              <path d="M16-43 L19-38 L22-43Z" fill="white" stroke="#cfe6d4" stroke-width="1.2" stroke-linejoin="round"/>
              <line x1="16" y1="-43" x2="21" y2="-43" stroke="white" stroke-width="1.5"/>
              <circle cx="18" cy="-50" r="1.5" fill="#1d7169" class="dot d1"/>
              <circle cx="24" cy="-50" r="1.5" fill="#1d7169" class="dot d2"/>
              <circle cx="30" cy="-50" r="1.5" fill="#1d7169" class="dot d3"/>
            </g>
          </g>

          <g class="dog">
            <ellipse cx="0" cy="7" rx="12" ry="2.5" fill="#000" opacity="0.12"/>
            <g class="tail-wrap" style="transform-origin:-11px -2px">
              <path d="M-11-2 q-7-4-13 0 q3-2 0-6" stroke="#b87c3a" stroke-width="3.5" fill="none" stroke-linecap="round"/>
            </g>
            <line x1="-5" y1="4" x2="-7" y2="13" stroke="#b87c3a" stroke-width="3" stroke-linecap="round"/>
            <line x1="-2" y1="4" x2="0" y2="13" stroke="#996622" stroke-width="3" stroke-linecap="round"/>
            <ellipse cx="0" cy="0" rx="14" ry="8" fill="#c98a4b"/>
            <ellipse cx="-2" cy="-2" rx="12" ry="5" fill="#dba365" opacity="0.65"/>
            <line x1="6" y1="4" x2="9" y2="13" stroke="#c98a4b" stroke-width="3" stroke-linecap="round"/>
            <line x1="10" y1="4" x2="12" y2="13" stroke="#996622" stroke-width="3" stroke-linecap="round"/>
            <circle cx="14" cy="-3" r="6.5" fill="#c98a4b"/>
            <ellipse cx="18" cy="-1" rx="3.5" ry="3" fill="#dba365"/>
            <path d="M10-8 q-2 5 0 8 q3-3 4-9z" fill="#996622"/>
            <circle cx="15" cy="-4" r="1.1" fill="#111"/>
            <circle cx="20" cy="-1.5" r="1" fill="#111"/>
            <path d="M18 1.5 q1.5 1.5 2.5 0" stroke="#111" stroke-width="0.8" fill="none" stroke-linecap="round"/>
            <rect x="8" y="-2" width="3" height="2.5" fill="#1d7169" rx="0.5"/>
            <circle cx="9.5" cy="0.8" r="0.7" fill="#ffd56b"/>
          </g>
        </svg>
      </div>

      <div class="scroll-hint" :style="{ opacity: scrollY > 80 ? 0 : 1 }">
        <div class="scroll-line"></div>
        <span>Scroll</span>
      </div>
    </section>

    <section class="editorial" data-reveal>
      <div class="ed-left">
        <p class="ed-label">What the data tells us</p>
        <h2 class="ed-headline">Wellbeing is a<br><em>shared experience.</em></h2>
      </div>
      <div class="ed-right">
        <p :style="{ fontSize: scaledPx(18) }">Around the country, people of every age experience periods of higher psychological distress. You are not alone — and small steps toward connection can change everything.</p>
        <div class="ed-stats">
          <div class="ed-stat">
            <span class="ed-stat-num">1 in 5</span>
            <span class="ed-stat-label" :style="{ fontSize: scaledPx(14) }">Australians experience loneliness</span>
          </div>
          <div class="ed-divider"></div>
          <div class="ed-stat">
            <span class="ed-stat-num">150+</span>
            <span class="ed-stat-label" :style="{ fontSize: scaledPx(14) }">Local events and places discovered</span>
          </div>
        </div>
      </div>
    </section>

    <section class="age-block" data-reveal>
      <div class="age-block-header">
        <p class="section-label">Understanding wellbeing across age groups</p>
        <h2>Select your age group</h2>
        <p class="section-sub" :style="{ fontSize: scaledPx(18) }">See how common this is and know you are not alone.</p>
      </div>

      <div class="age-selector-row">
        <div class="custom-select-wrap">
          <div class="custom-select" :class="{ open: selectOpen }" @click="selectOpen = !selectOpen">
            <span :style="{ fontSize: scaledPx(18) }">{{ selectedAgeGroup ? formatAgeGroup(selectedAgeGroup) : 'Choose your age group' }}</span>
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M6 9l6 6 6-6"/>
            </svg>
          </div>
          <div class="custom-options" v-if="selectOpen">
            <div
              v-for="item in distressData"
              :key="item.age_group"
              class="custom-option"
              :class="{ selected: selectedAgeGroup === item.age_group }"
              @click="selectedAgeGroup = item.age_group; selectOpen = false"
              :style="{ fontSize: scaledPx(16) }"
            >
              {{ formatAgeGroup(item.age_group) }}
            </div>
          </div>
        </div>
      </div>

      <p v-if="isLoading" class="loading-txt">Loading data…</p>
      <p v-if="loadError" class="error-txt">{{ loadError }}</p>

      <Transition name="fade-up">
        <div v-if="selectedRecord" class="age-result-panel">
          <div class="arp-left">
            <div class="arp-big">
              <span class="arp-num">{{ animatedCount }}</span>
              <span class="arp-denom">in 10</span>
            </div>
            <p class="arp-copy" :style="{ fontSize: scaledPx(20) }">people aged <strong>{{ formatAgeGroup(selectedRecord.age_group) }}</strong> experience higher levels of psychological distress.</p>
            <p class="arp-pct" :style="{ fontSize: scaledPx(16) }">That's approximately {{ selectedRecord.psychological_distress_percent }}% of this age group.</p>
            <p v-if="elderlyNote" class="arp-note" :style="{ fontSize: scaledPx(15) }">{{ elderlyNote }}</p>
            <p class="arp-source" :style="{ fontSize: scaledPx(13) }">{{ sourceText }}</p>
          </div>
          <div class="arp-right">
            <div class="people-grid" :key="selectedRecord.age_group">
              <div
                v-for="i in 10"
                :key="i"
                class="pg-person"
                :class="{ lit: i <= distressedCount }"
                :style="{ animationDelay: `${i * 60}ms` }"
              >
                <svg viewBox="0 0 24 28" width="36" height="44" fill="currentColor">
                  <circle cx="12" cy="6" r="5"/>
                  <path d="M2 26 q0-10 10-10 q10 0 10 10z"/>
                </svg>
              </div>
            </div>
            <p class="pg-legend"><span class="pg-legend-dot lit"></span> Experiencing distress &nbsp;&nbsp; <span class="pg-legend-dot"></span> Not experiencing distress</p>
          </div>
        </div>
      </Transition>
    </section>

    <section class="steps-block" data-reveal>
      <div class="steps-header">
        <p class="section-label">How we help</p>
        <h2>Small steps<br><em>can help.</em></h2>
        <p class="section-sub" :style="{ fontSize: scaledPx(17) }">Being part of your local community and finding places to connect can improve wellbeing and reduce feelings of isolation.</p>
      </div>

      <div class="steps-grid">
        <div
          v-for="(step, i) in steps"
          :key="step.title"
          class="step-tile"
          :style="{ '--i': i }"
          @mousemove="tiltTile"
          @mouseleave="untiltTile"
        >
          <div class="step-tile-inner">
            <div class="step-num">0{{ i + 1 }}</div>
            <div class="step-icon-wrap" :class="step.tone">
              <svg v-if="step.icon === 'pin'" viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/>
                <circle cx="12" cy="10" r="2.5"/>
              </svg>
              <svg v-else-if="step.icon === 'sparkle'" viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M5.6 18.4l2.8-2.8M15.6 8.4l2.8-2.8"/>
              </svg>
              <svg v-else-if="step.icon === 'access'" viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="4" r="2"/>
                <path d="M9 9h6l-1 5h-4l-2 7"/>
                <path d="M14 14a4 4 0 1 1-4 4"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 21s-7-4.5-7-11a5 5 0 0 1 9-3 5 5 0 0 1 9 3c0 6.5-7 11-7 11z"/>
              </svg>
            </div>
            <h3 :style="{ fontSize: scaledPx(22) }">{{ step.title }}</h3>
            <p :style="{ fontSize: scaledPx(15) }">{{ step.body }}</p>
            <div class="step-tile-shine"></div>
          </div>
        </div>
      </div>
    </section>

    <section class="cta-block" data-reveal>
      <div class="cta-bg-word" aria-hidden="true">LOCAL</div>
      <div class="cta-content">
        <p class="section-label">Ready to begin?</p>
        <h2>Your community<br>is waiting for you.</h2>
        <RouterLink to="/checkin" class="cta-btn" @mousemove="magnetMove" @mouseleave="magnetLeave">
          <span>Start your wellbeing check-in</span>
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M5 12h14M13 5l7 7-7 7"/>
          </svg>
        </RouterLink>
      </div>
    </section>

  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'

const API_URL = 'https://connectlocal.duckdns.org/api/suburbs/psychological-distress'

const selectedAgeGroup = ref('')
const distressData = ref([])
const sourceText = ref('ABS National Health Survey')
const elderlyHighlight = ref(null)
const isLoading = ref(false)
const loadError = ref('')
const selectOpen = ref(false)
const scrollY = ref(0)
const mouse = ref({ x: 0, y: 0 })
const animatedCount = ref(1)
const textScale = ref(100)
const scaledPx = (base) => `${(base * textScale.value) / 100}px`

const steps = [
  { icon: 'pin',     tone: 'mint',   title: 'Local places',      body: 'Find nearby places that feel familiar and easy to reach.' },
  { icon: 'sparkle', tone: 'yellow', title: 'Gentle activities',  body: 'Explore simple activities that do not feel too stressful.' },
  { icon: 'access',  tone: 'pink',   title: 'Comfort focused',    body: 'Consider access, comfort and ease before going out.' },
  { icon: 'heart',   tone: 'purple', title: 'Social connection',  body: 'Take small steps to reconnect with people around you.' }
]

const selectedRecord = computed(() => distressData.value.find(i => i.age_group === selectedAgeGroup.value))
const elderlyNote = computed(() => {
  if (!elderlyHighlight.value || !selectedRecord.value) return ''
  return selectedRecord.value.age_group === elderlyHighlight.value.age_group ? elderlyHighlight.value.note : ''
})
const distressedCount = computed(() => {
  if (!selectedRecord.value) return 1
  const count = Math.ceil(Number(selectedRecord.value.psychological_distress_percent) / 10)
  return Math.min(10, Math.max(1, count))
})

function formatAgeGroup(g) { return g === '65+' ? '65 years and over' : `${g} years` }
function handleMouse(e) { mouse.value = { x: e.clientX, y: e.clientY } }
function handleScroll() { scrollY.value = window.scrollY }
function magnetMove(e) { const r = e.currentTarget.getBoundingClientRect(); const x = e.clientX - r.left - r.width / 2; const y = e.clientY - r.top - r.height / 2; e.currentTarget.style.transform = `translate(${x * 0.22}px, ${y * 0.3}px)` }
function magnetLeave(e) { e.currentTarget.style.transform = '' }
function tiltTile(e) { const el = e.currentTarget; const r = el.getBoundingClientRect(); const x = (e.clientX - r.left) / r.width - 0.5; const y = (e.clientY - r.top) / r.height - 0.5; el.style.transform = `perspective(800px) rotateX(${-y * 7}deg) rotateY(${x * 9}deg) translateZ(6px)`; const shine = el.querySelector('.step-tile-shine'); if (shine) shine.style.background = `radial-gradient(180px at ${(x + 0.5) * 100}% ${(y + 0.5) * 100}%, rgba(255,255,255,0.5), transparent 60%)` }
function untiltTile(e) { e.currentTarget.style.transform = ''; const shine = e.currentTarget.querySelector('.step-tile-shine'); if (shine) shine.style.background = '' }

watch(distressedCount, val => {
  const start = animatedCount.value; const diff = val - start; let step = 0
  const id = setInterval(() => { step++; animatedCount.value = Math.round(start + diff * step / 18); if (step >= 18) { animatedCount.value = val; clearInterval(id) } }, 28)
})

let revealObserver = null
function setupReveal() {
  revealObserver = new IntersectionObserver(entries => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('in-view') }), { threshold: 0.12 })
  document.querySelectorAll('[data-reveal]').forEach(el => revealObserver.observe(el))
}

async function fetchData() {
  isLoading.value = true; loadError.value = ''
  try {
    const res = await fetch(API_URL)
    if (!res.ok) throw new Error()
    const data = await res.json()
    distressData.value = data.data || []
    elderlyHighlight.value = data.elderly_highlight || null
    if (data.source && data.year) { sourceText.value = data.note ? `${data.source}, ${data.note}, ${data.year}` : `${data.source}, ${data.year}` }
  } catch { loadError.value = 'Unable to load wellbeing data right now.' }
  finally { isLoading.value = false }
}

onMounted(() => { fetchData(); setupReveal(); window.addEventListener('scroll', handleScroll, { passive: true }) })
onBeforeUnmount(() => { if (revealObserver) revealObserver.disconnect(); window.removeEventListener('scroll', handleScroll) })
</script>

<style scoped>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.page {
  min-height: 100vh; background: #f2faf0; color: #1a2e1e;
  font-family: 'Georgia', serif; overflow-x: hidden; position: relative;
}

.noise {
  position: fixed; inset: 0; z-index: 1000; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
  background-size: 180px; opacity: 0.45;
}

.orb { position: fixed; border-radius: 50%; pointer-events: none; z-index: 0; filter: blur(80px); }
.orb-1 { width: 500px; height: 500px; background: rgba(90,180,110,0.2); top: -120px; left: -80px; animation: orb-drift 20s ease-in-out infinite alternate; }
.orb-2 { width: 400px; height: 400px; background: rgba(255,180,140,0.14); bottom: 10%; right: -80px; animation: orb-drift 26s ease-in-out infinite alternate-reverse; }
@keyframes orb-drift { 0%{transform:translate(0,0) scale(1)} 100%{transform:translate(50px,60px) scale(1.12)} }

.nav {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 28px 52px; transition: background 0.5s, padding 0.4s, box-shadow 0.4s;
}
.nav.scrolled { background: rgba(242,250,240,0.88); backdrop-filter: blur(18px); padding: 18px 52px; box-shadow: 0 1px 0 rgba(29,113,105,0.12); }
.nav-brand { display: flex; align-items: center; gap: 12px; text-decoration: none; }
.nav-logo { width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg,#0a9b8a,#056b5e); color: white; display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 16px rgba(7,141,127,0.3); }
.nav-wordmark { font-family: Georgia,serif; font-size: 22px; color: #1a2e1e; }
.nav-wordmark em { color: #0a9b8a; font-style: italic; }
.nav-links { display: flex; gap: 36px; align-items: center; }
.nav-links a { font-family: system-ui,sans-serif; font-size: 15px; font-weight: 600; color: #3a5a3e; text-decoration: none; transition: color 0.2s; }
.nav-links a:hover { color: #0a9b8a; }
.nav-links .router-link-active { color: #0a9b8a; }
.nav-link-coming { font-family: system-ui,sans-serif; font-size: 15px; font-weight: 600; color: #3a5a3e; cursor: default; }
.nav-cta { display: inline-flex; align-items: center; gap: 8px; font-family: system-ui,sans-serif; font-size: 14px; font-weight: 700; color: #0a9b8a; text-decoration: none; padding: 10px 22px; border: 1.5px solid #0a9b8a; border-radius: 999px; transition: all 0.3s; }
.nav-cta:hover { background: #0a9b8a; color: white; }

.a11y-bar {
  position: fixed; top: 86px; right: 0; left: 0; z-index: 90;
  background: rgba(255,255,255,0.92); backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(29,113,105,0.1);
  box-shadow: 0 4px 16px rgba(0,0,0,0.04);
}
.a11y-inner { display: flex; align-items: center; justify-content: flex-end; padding: 10px 52px; }
.text-size-control {
  display: inline-flex; align-items: center; gap: 12px;
  background: rgba(255,255,255,0.9); backdrop-filter: blur(10px);
  border: 1.5px solid rgba(29,113,105,0.18); border-radius: 999px; padding: 8px 18px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.06);
}
.a-small { font-family: Georgia,serif; font-size: 13px; font-weight: 700; color: #0a9b8a; line-height: 1; }
.a-large { font-family: Georgia,serif; font-size: 22px; font-weight: 700; color: #0a9b8a; line-height: 1; }
.text-slider { -webkit-appearance: none; appearance: none; width: 120px; height: 4px; background: #d1e8d4; border-radius: 999px; outline: none; cursor: pointer; }
.text-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 22px; height: 22px; border-radius: 50%; background: #0a9b8a; box-shadow: 0 2px 8px rgba(10,155,138,0.4); cursor: pointer; transition: transform 0.2s; }
.text-slider::-webkit-slider-thumb:hover { transform: scale(1.15); }
.text-slider:focus-visible { outline: 3px solid #0a9b8a; outline-offset: 3px; }
.scale-pct { font-size: 13px; font-weight: 700; color: #6a8e6e; min-width: 38px; }

.hero {
  position: relative; min-height: 100vh;
  display: grid; grid-template-columns: 1fr 1fr;
  align-items: center; overflow: hidden;
  padding: 180px 52px 80px; gap: 40px;
}

.hero-bg-text {
  position: absolute; left: -2%; top: 50%; transform: translateY(-50%);
  font-family: Georgia,serif; font-size: clamp(120px,18vw,220px);
  font-weight: 700; font-style: italic; color: rgba(10,155,138,0.055);
  white-space: nowrap; pointer-events: none; letter-spacing: -0.04em; line-height: 1; user-select: none;
}

.hero-tag {
  position: absolute; z-index: 10;
  display: inline-flex; align-items: center; gap: 8px;
  font-family: system-ui,sans-serif; font-size: 13px; font-weight: 600;
  color: #1d7169; letter-spacing: 0.05em;
  background: rgba(255,255,255,0.82); backdrop-filter: blur(10px);
  border: 1px solid rgba(29,113,105,0.18); padding: 8px 16px; border-radius: 999px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.06);
  transition: transform 0.6s cubic-bezier(0.22,1,0.36,1);
}
.tag-dot { width: 6px; height: 6px; border-radius: 50%; background: #0a9b8a; animation: blink 2s ease-in-out infinite; }
.tag-1 { top: 22%; left: 46%; }
.tag-2 { top: 36%; right: 4%; }
.tag-3 { bottom: 22%; left: 52%; }
@keyframes blink { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.4;transform:scale(1.5)} }

.hero-content { position: relative; z-index: 2; }
.hero-eyebrow { font-family: system-ui,sans-serif; font-size: 13px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #0a9b8a; display: flex; align-items: center; gap: 12px; margin-bottom: 28px; opacity: 0; animation: fade-up 0.8s 0.2s forwards; }
.hero-eyebrow::before { content: ''; display: block; width: 32px; height: 1px; background: #0a9b8a; }
.hero-headline { font-family: Georgia,serif; font-size: clamp(54px,7vw,96px); font-weight: 700; line-height: 1.02; color: #0f1e12; margin-bottom: 36px; }
.hero-headline .line { display: block; opacity: 0; transform: translateY(36px); animation: fade-up 0.9s cubic-bezier(0.22,1,0.36,1) forwards; }
.hero-headline .line:nth-child(1) { animation-delay: 0.35s; }
.hero-headline .line-accent { font-style: italic; color: #0a9b8a; animation-delay: 0.5s; }
.hero-headline .line:nth-child(3) { animation-delay: 0.65s; }
.hero-sub { opacity: 0; animation: fade-up 0.8s 0.9s forwards; margin-bottom: 44px; }
.hero-sub p { font-family: system-ui,sans-serif; font-size: 18px; line-height: 1.7; color: #4a6a4e; margin-bottom: 8px; }
.hero-cta { display: inline-flex; align-items: center; gap: 14px; font-family: system-ui,sans-serif; font-size: 16px; font-weight: 700; background: linear-gradient(135deg,#0a9b8a,#056b5e); color: white; text-decoration: none; padding: 18px 32px; border-radius: 4px; box-shadow: 0 16px 40px rgba(10,155,138,0.28); opacity: 0; animation: fade-up 0.8s 1.1s forwards; transition: transform 0.3s, box-shadow 0.3s; }
.hero-cta:hover { box-shadow: 0 22px 48px rgba(10,155,138,0.36); }
.hero-cta svg { transition: transform 0.3s; }
.hero-cta:hover svg { transform: translateX(5px); }

.hero-scene { position: relative; z-index: 2; width: 100%; height: 640px; }
.scene-svg { width: 100%; height: 100%; }

.scroll-hint { position: absolute; bottom: 40px; left: 52px; display: flex; align-items: center; gap: 14px; font-family: system-ui,sans-serif; font-size: 12px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: #6a8e6e; transition: opacity 0.4s; animation: fade-up 0.8s 1.6s both; }
.scroll-line { width: 1px; height: 48px; background: linear-gradient(to bottom,transparent,#0a9b8a); animation: scroll-grow 2s ease-in-out infinite; }
@keyframes scroll-grow { 0%,100%{height:36px;opacity:0.5} 50%{height:56px;opacity:1} }

.editorial { display: grid; grid-template-columns: 1fr 1fr; gap: 80px; padding: 120px 52px; border-top: 1px solid rgba(29,113,105,0.12); opacity: 0; transform: translateY(40px); transition: all 0.9s cubic-bezier(0.22,1,0.36,1); }
.editorial.in-view { opacity: 1; transform: none; }
.ed-label { font-family: system-ui,sans-serif; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #0a9b8a; margin-bottom: 24px; }
.ed-headline { font-family: Georgia,serif; font-size: clamp(36px,4vw,58px); font-weight: 700; line-height: 1.1; color: #0f1e12; }
.ed-headline em { color: #0a9b8a; font-style: italic; }
.ed-right { display: flex; flex-direction: column; justify-content: center; gap: 40px; }
.ed-right > p { font-family: system-ui,sans-serif; font-size: 18px; line-height: 1.75; color: #4a6a4e; }
.ed-stats { display: flex; align-items: center; gap: 32px; }
.ed-stat { display: flex; flex-direction: column; gap: 6px; }
.ed-stat-num { font-family: Georgia,serif; font-size: 42px; font-weight: 700; color: #0a9b8a; line-height: 1; }
.ed-stat-label { font-family: system-ui,sans-serif; font-size: 14px; color: #6a8e6e; max-width: 160px; line-height: 1.4; }
.ed-divider { width: 1px; height: 60px; background: rgba(29,113,105,0.2); }

.age-block { padding: 100px 52px; background: rgba(255,255,255,0.55); backdrop-filter: blur(12px); border-top: 1px solid rgba(29,113,105,0.1); border-bottom: 1px solid rgba(29,113,105,0.1); opacity: 0; transform: translateY(40px); transition: all 0.9s cubic-bezier(0.22,1,0.36,1); }
.age-block.in-view { opacity: 1; transform: none; }
.age-block-header { margin-bottom: 56px; }
.section-label { font-family: system-ui,sans-serif; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #0a9b8a; margin-bottom: 16px; }
.age-block-header h2 { font-family: Georgia,serif; font-size: clamp(32px,4vw,52px); font-weight: 700; color: #0f1e12; line-height: 1.1; margin-bottom: 14px; }
.section-sub { font-family: system-ui,sans-serif; font-size: 18px; color: #4a6a4e; line-height: 1.65; }

.age-selector-row { margin-bottom: 48px; }
.custom-select-wrap { position: relative; display: inline-block; min-width: 340px; }
.custom-select { display: flex; align-items: center; justify-content: space-between; padding: 18px 24px; cursor: pointer; border: 1.5px solid rgba(29,113,105,0.3); border-radius: 4px; background: white; font-family: Georgia,serif; font-size: 18px; color: #1a2e1e; transition: border-color 0.25s, box-shadow 0.25s; user-select: none; }
.custom-select:hover, .custom-select.open { border-color: #0a9b8a; box-shadow: 0 0 0 3px rgba(10,155,138,0.1); }
.custom-select svg { color: #0a9b8a; transition: transform 0.3s; }
.custom-select.open svg { transform: rotate(180deg); }
.custom-options { position: absolute; top: calc(100% + 6px); left: 0; right: 0; background: white; border: 1.5px solid rgba(10,155,138,0.25); border-radius: 4px; z-index: 50; overflow: hidden; box-shadow: 0 12px 32px rgba(0,0,0,0.1); }
.custom-option { padding: 14px 24px; cursor: pointer; font-family: system-ui,sans-serif; font-size: 16px; color: #2a4a2e; transition: background 0.15s; }
.custom-option:hover { background: #f0faf0; }
.custom-option.selected { color: #0a9b8a; font-weight: 700; }
.loading-txt, .error-txt { font-family: system-ui,sans-serif; font-size: 15px; color: #6a8e6e; margin-bottom: 20px; }
.error-txt { color: #b3261e; }

.age-result-panel { display: grid; grid-template-columns: 1fr 1fr; gap: 60px; align-items: start; padding: 52px; background: white; border: 1px solid rgba(29,113,105,0.12); border-radius: 4px; box-shadow: 0 24px 60px rgba(0,0,0,0.06); }
.arp-big { display: flex; align-items: baseline; gap: 16px; margin-bottom: 20px; }
.arp-num { font-family: Georgia,serif; font-size: 100px; font-weight: 700; line-height: 1; color: #0a9b8a; }
.arp-denom { font-family: Georgia,serif; font-size: 32px; color: #4a6a4e; font-style: italic; }
.arp-copy { font-family: system-ui,sans-serif; font-size: 20px; line-height: 1.6; color: #1a2e1e; margin-bottom: 14px; }
.arp-pct { font-family: system-ui,sans-serif; font-size: 16px; color: #4a6a4e; margin-bottom: 10px; }
.arp-note { font-family: system-ui,sans-serif; font-size: 15px; color: #0a9b8a; font-weight: 700; margin-bottom: 10px; }
.arp-source { font-family: system-ui,sans-serif; font-size: 13px; color: #8aaa8e; margin-top: 16px; line-height: 1.5; }

.people-grid { display: grid; grid-template-columns: repeat(5,1fr); gap: 12px; margin-bottom: 16px; }
.pg-person { display: flex; align-items: center; justify-content: center; color: #d8e8d8; opacity: 0; transform: translateY(12px) scale(0.8); animation: pop-in 0.5s cubic-bezier(0.22,1.6,0.36,1) forwards; transition: color 0.3s, transform 0.25s; }
.pg-person.lit { color: #0a9b8a; filter: drop-shadow(0 3px 8px rgba(10,155,138,0.3)); }
.pg-person.lit:hover { transform: translateY(-4px) scale(1.12); }
.pg-legend { font-family: system-ui,sans-serif; font-size: 12px; color: #8aaa8e; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.pg-legend-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #d8e8d8; }
.pg-legend-dot.lit { background: #0a9b8a; }

.steps-block { padding: 120px 52px; opacity: 0; transform: translateY(40px); transition: all 0.9s cubic-bezier(0.22,1,0.36,1); }
.steps-block.in-view { opacity: 1; transform: none; }
.steps-header { max-width: 560px; margin-bottom: 72px; }
.steps-header h2 { font-family: Georgia,serif; font-size: clamp(36px,4.5vw,60px); font-weight: 700; line-height: 1.08; color: #0f1e12; margin-bottom: 20px; }
.steps-header h2 em { color: #0a9b8a; font-style: italic; }
.steps-header .section-sub { font-size: 17px; color: #4a6a4e; line-height: 1.7; font-family: system-ui,sans-serif; }
.steps-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 20px; }
.step-tile { border-radius: 2px; transform-style: preserve-3d; transition: transform 0.4s cubic-bezier(0.22,1,0.36,1); opacity: 0; transform: translateY(28px); animation: pop-tile 0.7s calc(var(--i) * 100ms) forwards; }
@keyframes pop-tile { to { opacity:1; transform:none; } }
.step-tile-inner { position: relative; overflow: hidden; padding: 40px 28px; background: white; border: 1px solid rgba(29,113,105,0.1); border-radius: 2px; box-shadow: 0 8px 24px rgba(0,0,0,0.05); height: 100%; }
.step-num { font-family: Georgia,serif; font-size: 13px; font-weight: 700; color: rgba(10,155,138,0.35); letter-spacing: 0.1em; margin-bottom: 28px; }
.step-icon-wrap { width: 58px; height: 58px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 24px; position: relative; }
.step-icon-wrap::before { content: ''; position: absolute; inset: -5px; border: 1.5px solid currentColor; border-radius: 50%; opacity: 0.2; }
.mint   { background: #d6f4e7; color: #1d7169; }
.yellow { background: #fff3c2; color: #b88a00; }
.pink   { background: #ffded5; color: #c44a2c; }
.purple { background: #e6dcff; color: #5b3fb6; }
.step-tile h3 { font-family: Georgia,serif; font-size: 22px; font-weight: 700; color: #0f1e12; margin-bottom: 12px; }
.step-tile p { font-family: system-ui,sans-serif; font-size: 15px; line-height: 1.6; color: #4a6a4e; }
.step-tile-shine { position: absolute; inset: 0; pointer-events: none; border-radius: 2px; transition: background 0.2s; }

.cta-block { position: relative; overflow: hidden; padding: 160px 52px; background: linear-gradient(160deg,#e4f5e0,#c8edc8); border-top: 1px solid rgba(29,113,105,0.14); text-align: center; opacity: 0; transform: translateY(40px); transition: all 0.9s cubic-bezier(0.22,1,0.36,1); }
.cta-block.in-view { opacity: 1; transform: none; }
.cta-bg-word { position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%); font-family: Georgia,serif; font-size: clamp(100px,16vw,200px); font-weight: 700; font-style: italic; color: rgba(10,155,138,0.06); white-space: nowrap; pointer-events: none; user-select: none; letter-spacing: -0.04em; }
.cta-content { position: relative; z-index: 2; }
.cta-block .section-label { margin-bottom: 20px; }
.cta-block h2 { font-family: Georgia,serif; font-size: clamp(40px,6vw,76px); font-weight: 700; line-height: 1.05; color: #0f1e12; margin-bottom: 52px; }
.cta-btn { display: inline-flex; align-items: center; gap: 14px; font-family: system-ui,sans-serif; font-size: 16px; font-weight: 700; background: #0a9b8a; color: white; text-decoration: none; padding: 20px 38px; border-radius: 4px; box-shadow: 0 16px 40px rgba(10,155,138,0.3); transition: transform 0.3s, box-shadow 0.3s; }
.cta-btn:hover { box-shadow: 0 24px 48px rgba(10,155,138,0.4); }
.cta-btn svg { transition: transform 0.3s; }
.cta-btn:hover svg { transform: translateX(5px); }

@keyframes fade-up { from{opacity:0;transform:translateY(24px)} to{opacity:1;transform:none} }
@keyframes pop-in { to{opacity:1;transform:none} }

.sun-rays { animation: sun-spin 60s linear infinite; transform-origin: 400px 110px; }
@keyframes sun-spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
.cloud.c1 { animation: cloud-drift 40s linear infinite; }
.cloud.c2 { animation: cloud-drift 56s linear infinite reverse; }
@keyframes cloud-drift { 0%{transform:translateX(-80px)} 100%{transform:translateX(620px)} }
.bird.b1 { animation: bird1 16s linear infinite; }
.bird.b2 { animation: bird2 22s 5s linear infinite; }
@keyframes bird1 { 0%{transform:translate(-30px,200px)} 100%{transform:translate(560px,90px)} }
@keyframes bird2 { 0%{transform:translate(-30px,260px) scale(0.75)} 100%{transform:translate(580px,150px) scale(1)} }
.tree.t1 { animation: sway 4.5s ease-in-out infinite; transform-box: fill-box; }
.tree.t2 { animation: sway 5.5s ease-in-out infinite reverse; transform-box: fill-box; }
@keyframes sway { 0%,100%{transform:rotate(-1.8deg)} 50%{transform:rotate(1.8deg)} }
.smoke.s1 { animation: smoke-up 4s ease-out infinite; transform-box: fill-box; transform-origin: center; }
.smoke.s2 { animation: smoke-up 4s 1.3s ease-out infinite; transform-box: fill-box; transform-origin: center; }
.smoke.s3 { animation: smoke-up 4s 2.6s ease-out infinite; transform-box: fill-box; transform-origin: center; }
@keyframes smoke-up { 0%{transform:translateY(0) scale(1);opacity:0.6} 100%{transform:translateY(-20px) scale(1.8);opacity:0} }
.lamp { animation: lamp-glow 3.5s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
@keyframes lamp-glow { 0%,100%{opacity:0.8} 50%{opacity:1;filter:drop-shadow(0 0 5px #ffd56b)} }
.butterfly { animation: bf-fly 16s ease-in-out infinite; transform-box: fill-box; }
.bf-wings  { animation: bf-flap 0.2s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
@keyframes bf-flap { 0%,100%{transform:scaleX(1)} 50%{transform:scaleX(0.35)} }
@keyframes bf-fly { 0%{transform:translate(160px,470px)} 25%{transform:translate(200px,440px)} 50%{transform:translate(270px,468px)} 75%{transform:translate(330px,430px)} 100%{transform:translate(160px,470px)} }
.person.p1 { animation: p1-walk 12s ease-in-out infinite; transform-box: fill-box; }
.person.p2 { animation: p2-walk 12s ease-in-out infinite; transform-box: fill-box; }
.dog { animation: dog-walk 12s ease-in-out infinite; transform-box: fill-box; }
@keyframes p1-walk { 0%,100%{transform:translate(108px,480px)} 25%,75%{transform:translate(240px,480px)} }
@keyframes p2-walk { 0%,100%{transform:translate(468px,480px)} 25%,75%{transform:translate(336px,480px)} }
@keyframes dog-walk { 0%,100%{transform:translate(500px,496px)} 25%,75%{transform:translate(368px,496px)} }
.leg.pl1-lf, .leg.pl2-lf { transform-origin:-1px 0; transform-box:fill-box; animation: walk-a 12s linear infinite; }
.leg.pl1-lb, .leg.pl2-lb { transform-origin:1px 0; transform-box:fill-box; animation: walk-b 12s linear infinite; }
.arm.pl1-ab { animation: walk-a 12s linear infinite; transform-box:fill-box; }
.arm.pl2-ab { animation: walk-b 12s linear infinite; transform-box:fill-box; }
.arm.pl2-af { transform-origin:-9px -16px; transform-box:fill-box; animation: walk-a 12s linear infinite; }
@keyframes walk-a { 0%{transform:rotate(-22deg)} 4%{transform:rotate(22deg)} 8%{transform:rotate(-22deg)} 12%{transform:rotate(22deg)} 16%{transform:rotate(-22deg)} 20%{transform:rotate(22deg)} 25%,75%{transform:rotate(0)} 79%{transform:rotate(22deg)} 83%{transform:rotate(-22deg)} 87%{transform:rotate(22deg)} 91%{transform:rotate(-22deg)} 95%{transform:rotate(22deg)} 100%{transform:rotate(-22deg)} }
@keyframes walk-b { 0%{transform:rotate(22deg)} 4%{transform:rotate(-22deg)} 8%{transform:rotate(22deg)} 12%{transform:rotate(-22deg)} 16%{transform:rotate(22deg)} 20%{transform:rotate(-22deg)} 25%,75%{transform:rotate(0)} 79%{transform:rotate(-22deg)} 83%{transform:rotate(22deg)} 87%{transform:rotate(-22deg)} 91%{transform:rotate(22deg)} 95%{transform:rotate(-22deg)} 100%{transform:rotate(22deg)} }
.wave-arm { animation: wave 12s ease-in-out infinite; transform-box:fill-box; }
@keyframes wave { 0%,24%,76%,100%{transform:rotate(0)} 28%{transform:rotate(155deg)} 36%{transform:rotate(145deg)} 44%{transform:rotate(165deg)} 52%{transform:rotate(145deg)} 60%{transform:rotate(165deg)} 68%{transform:rotate(155deg)} }
.speech { opacity:0; transform-box:fill-box; animation: sp-pop 12s ease-in-out infinite; }
.speech.sp2 { animation-delay:0.4s; }
@keyframes sp-pop { 0%,30%,76%,100%{opacity:0;transform:translateY(5px) scale(0.6)} 36%,70%{opacity:1;transform:none} }
.dot { animation: dot-bounce 1s ease-in-out infinite; transform-box:fill-box; }
.dot.d1{animation-delay:0s} .dot.d2{animation-delay:0.18s} .dot.d3{animation-delay:0.36s}
@keyframes dot-bounce { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-2.5px)} }
.tail-wrap { animation: tail-wag 0.34s ease-in-out infinite; transform-box:fill-box; }
@keyframes tail-wag { 0%,100%{transform:rotate(-28deg)} 50%{transform:rotate(28deg)} }
.steam path { animation: steam-up 2.6s ease-in-out infinite; transform-box:fill-box; }
.steam path:nth-child(2) { animation-delay:0.65s; }
@keyframes steam-up { 0%{opacity:0;transform:translateY(2px)} 50%{opacity:0.8} 100%{opacity:0;transform:translateY(-7px)} }

.fade-up-enter-active { transition: all 0.55s cubic-bezier(0.22,1,0.36,1); }
.fade-up-leave-active { transition: all 0.3s ease; }
.fade-up-enter-from  { opacity:0; transform:translateY(18px); }
.fade-up-leave-to    { opacity:0; transform:translateY(-10px); }

@media (max-width: 1000px) {
  .nav { padding: 20px 24px; }
  .nav.scrolled { padding: 14px 24px; }
  .nav-links { display: none; }
  .a11y-inner { padding: 10px 20px; }
  .hero { grid-template-columns: 1fr; padding: 180px 24px 60px; }
  .hero-scene { height: 420px; }
  .hero-tag { display: none; }
  .hero-bg-text { font-size: 80px; }
  .editorial { grid-template-columns: 1fr; padding: 80px 24px; gap: 48px; }
  .age-block { padding: 80px 24px; }
  .age-result-panel { grid-template-columns: 1fr; padding: 32px 24px; gap: 40px; }
  .steps-block { padding: 80px 24px; }
  .steps-grid { grid-template-columns: 1fr 1fr; }
  .cta-block { padding: 100px 24px; }
  .arp-num { font-size: 72px; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; transition-duration: 0.01ms !important; }
}
</style>