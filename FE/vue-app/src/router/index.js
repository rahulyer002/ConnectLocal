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

    { path: '/best-time', component: BestTimePage },
    { path: '/best-time-result', component: BestTimeResultPage },
    { path: '/best-time-week', component: BestTimeWeekPage },
    { path: '/welcoming-spaces', component: WelcomingSpacesPage },

    { path: '/:pathMatch(.*)*', redirect: '/home' },
  ],
})

export default router