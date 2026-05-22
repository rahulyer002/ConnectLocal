import { createRouter, createWebHistory } from 'vue-router'

import HomePage from '../pages/HomePage.vue'
import DiscoverPage from '../pages/DiscoverPage.vue'
import CheckinPage from '../pages/CheckinPage.vue'
import CheckinFormPage from '../pages/CheckinFormPage.vue'
import ResultsPage from '../pages/ResultsPage.vue'
import EventDetailsPage from '../pages/EventDetailsPage.vue'
import JourneySupportPage from '../pages/JourneySupportPage.vue'
import BestTimePage from '../pages/BestTimePage.vue'
import LoginPage from '../pages/LoginPage.vue'
import SuburbExplorerPage from '../pages/SuburbExplorerPage.vue'

const AUTH_KEY = 'connectlocal_logged_in'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },

    {
      path: '/login',
      component: LoginPage,
      meta: { public: true }
    },

    { path: '/home', component: HomePage },
    { path: '/discover', component: DiscoverPage },
    { path: '/journey', component: JourneySupportPage },
    { path: '/events/:id', component: EventDetailsPage },
    { path: '/checkin', component: CheckinPage },
    { path: '/checkin-form', component: CheckinFormPage },
    { path: '/results', component: ResultsPage },
    { path: '/best-time', component: BestTimePage },

    // Legacy sub-routes redirect to the unified Best Time page anchors.
    { path: '/best-time/now', redirect: { path: '/best-time', hash: '#step-where' } },
    { path: '/best-time/week', redirect: { path: '/best-time', hash: '#step-when' } },
    { path: '/welcoming-spaces', redirect: { path: '/best-time', hash: '#step-community' } },

    { path: '/suburb-explorer', component: SuburbExplorerPage },

    { path: '/:pathMatch(.*)*', redirect: '/home' }
  ],
})

router.beforeEach((to, from, next) => {
  const isPublicPage = to.meta.public === true
  const isLoggedIn = sessionStorage.getItem(AUTH_KEY) === 'true'

  if (isPublicPage) {
    next()
    return
  }

  if (!isLoggedIn) {
    next({
      path: '/login',
      query: {
        redirect: to.fullPath
      }
    })
    return
  }

  next()
})

export default router