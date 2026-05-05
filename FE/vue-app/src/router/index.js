import { createRouter, createWebHistory } from 'vue-router'

import HomePage from '../pages/HomePage.vue'
import DiscoverPage from '../pages/DiscoverPage.vue'
import CheckinPage from '../pages/CheckinPage.vue'
import CheckinFormPage from '../pages/CheckinFormPage.vue'
import ResultsPage from '../pages/ResultsPage.vue'
import EventDetailsPage from '../pages/EventDetailsPage.vue'
import JourneySupportPage from '../pages/JourneySupportPage.vue'
import BestTimePage from '../pages/BestTimePage.vue'
import BestTimeNowPage from '../pages/BestTimeNowPage.vue'
import BestTimeWeekPage from '../pages/BestTimeWeekPage.vue'
import WelcomingSpacesPage from '../pages/WelcomingSpacesPage.vue' 
import LoginPage from '../pages/LoginPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
  { path: '/login', component: LoginPage },

    { path: '/home', component: HomePage },
    { path: '/discover', component: DiscoverPage },
    { path: '/journey', component: JourneySupportPage },
    { path: '/events/:id', component: EventDetailsPage },
    { path: '/checkin', component: CheckinPage },
    { path: '/checkin/form', component: CheckinFormPage },
    { path: '/results', component: ResultsPage },

   { path: '/best-time', component: BestTimePage },
{ path: '/best-time/now', component: BestTimeNowPage },
{ path: '/best-time/week', component: BestTimeWeekPage },
{ path: '/welcoming-spaces', component: WelcomingSpacesPage },

    { path: '/:pathMatch(.*)*', redirect: '/home' },
  ],
})

export default router
