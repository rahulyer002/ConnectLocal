<template>
  <RouterView />
  <ChatbotButton />
</template>

<script setup>
import ChatbotButton from './components/ChatbotButton.vue'
</script>

<style>
:root {
  --text-scale: 1;
}
</style>