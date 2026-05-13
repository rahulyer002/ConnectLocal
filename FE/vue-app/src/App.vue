<template>
  <BestTimeNav v-if="isBestTimeRoute" />
  <TextSizeSlider v-if="showSlider" />
  <ChatbotButton />   
  <RouterView />
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import BestTimeNav from './components/BestTimeNav.vue'
import TextSizeSlider from './components/TextSizeSlider.vue'
import ChatbotButton from './components/ChatbotButton.vue'

const route = useRoute()

const isBestTimeRoute = computed(() => {
  const p = route.path || ''
  return p.startsWith('/best-time') || p === '/welcoming-spaces'
})

// Hide slider on intensive form pages where it adds noise; show everywhere else
const showSlider = computed(() => {
  const p = route.path || ''
  return p !== '/checkin/form' && p !== '/results' && p !== '/journey' && p !== '/login'
})
</script>

<style>
:root { --text-scale: 1; }
</style>