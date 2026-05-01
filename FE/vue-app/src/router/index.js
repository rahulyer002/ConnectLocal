import { createRouter, createWebHistory } from 'vue-router'

import HomePage from '../pages/HomePage.vue'
import DiscoverPage from '../pages/DiscoverPage.vue'
import CheckinPage from '../pages/CheckinPage.vue'
import CheckinFormPage from '../pages/CheckinFormPage.vue'
import ResultsPage from '../pages/ResultsPage.vue'
import EventDetailsPage from '../pages/EventDetailsPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/home' },

    { path: '/home', component: HomePage },
    { path: '/discover', component: DiscoverPage },
    { path: '/events/:id', component: EventDetailsPage },
    { path: '/checkin', component: CheckinPage },
    { path: '/checkin-form', component: CheckinFormPage },
    { path: '/results', component: ResultsPage },

    { path: '/:pathMatch(.*)*', redirect: '/home' },
  ],
})

export default router