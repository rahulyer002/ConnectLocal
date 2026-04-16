import { createRouter, createWebHistory } from 'vue-router'
import DiscoverPage from '../pages/DiscoverPage.vue'
import CheckinPage from '../pages/CheckinPage.vue'
import ResultsPage from '../pages/ResultsPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/discover' },
    { path: '/discover', component: DiscoverPage },
    { path: '/checkin', component: CheckinPage },
    { path: '/results', component: ResultsPage },
  ],
})

export default router
