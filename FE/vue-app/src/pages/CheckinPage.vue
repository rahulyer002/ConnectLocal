<template>
  <MainLayout>
    <section class="placeholder-page">
      <h2>Check-in</h2>
      <p>This area is ready for your check-in widgets and form content.</p>
    </section>
  </MainLayout>
</template>

<script setup>
import MainLayout from '../layouts/MainLayout.vue'
</script>

<style scoped>
.placeholder-page {
  margin: 28px;
  border-radius: var(--radius-xl);
  border: 2px dashed #cfd1e1;
  background: #fff;
  padding: 30px;
}

.placeholder-page h2 {
  margin: 0 0 8px;
  font-family: 'Fraunces', serif;
  font-size: clamp(30px, 3vw, 42px);
}

.placeholder-page p {
  margin: 0;
  font-size: 18px;
  color: #555973;
}
</style>
