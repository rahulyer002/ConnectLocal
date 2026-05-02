import { createRouter, createWebHistory } from 'vue-router'

import HomePage from '../pages/HomePage.vue'
import DiscoverPage from '../pages/DiscoverPage.vue'
import CheckinPage from '../pages/CheckinPage.vue'
import CheckinFormPage from '../pages/CheckinFormPage.vue'
import ResultsPage from '../pages/ResultsPage.vue'
import EventDetailsPage from '../pages/EventDetailsPage.vue'
import AboutPage from '../pages/AboutPage.vue'
import ResourcesPage from '../pages/ResourcesPage.vue'
import BestTimePage from '../pages/BestTimePage.vue'
import BestTimeResultPage from '../pages/BestTimeResultPage.vue'
import BestTimeWeekPage from '../pages/BestTimeWeekPage.vue'
import WelcomingSpacesPage from '../pages/WelcomingSpacesPage.vue'

const router = createRouter({
  history: createWebHistory(),

  routes: [
    { path: '/', redirect: '/home' },

    { path: '/home', component: HomePage },
    { path: '/discover', component: DiscoverPage },
    { path: '/events/:id', component: EventDetailsPage },

    { path: '/about', component: AboutPage },
    { path: '/resources', component: ResourcesPage },

    { path: '/checkin', component: CheckinPage },
    { path: '/checkin-form', component: CheckinFormPage },
    { path: '/results', component: ResultsPage },

    // Epic 4 — Personalised Timing & Resonance Engine
    { path: '/best-time', component: BestTimePage },
    { path: '/best-time/result', component: BestTimeResultPage },
    { path: '/best-time/week', component: BestTimeWeekPage },
    { path: '/best-time/welcoming', component: WelcomingSpacesPage },

    // Backup routes, in case old buttons still use these paths
    { path: '/best-time-result', redirect: '/best-time/result' },
    { path: '/best-time-week', redirect: '/best-time/week' },
    { path: '/welcoming-spaces', redirect: '/best-time/welcoming' },

    { path: '/:pathMatch(.*)*', redirect: '/home' },
  ],
})

export default router