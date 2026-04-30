<template>
  <MainLayout>
    <section class="details-page">
      <article class="details-card">
        <RouterLink class="back-link" to="/discover">← Back to Discover</RouterLink>
        <h2>Event ID: {{ route.params.id }}</h2>
      </article>
    </section>
  </MainLayout>
</template>

<script setup>
import { useRoute } from "vue-router";
import MainLayout from "../layouts/MainLayout.vue";

const route = useRoute();
</script>

<style scoped>
.details-page {
  padding: 18px;
}

.details-card {
  background: var(--panel-2);
  border: 2px solid #cbccdf;
  border-radius: var(--radius-xl);
  padding: 20px;
}

.back-link {
  display: inline-block;
  margin-bottom: 12px;
  font-weight: 700;
  color: #06786f;
}

h2 {
  margin: 0;
  font-family: "Fraunces", serif;
  font-size: clamp(calc(28px * var(--font-scale)), calc(3vw * var(--font-scale)), calc(44px * var(--font-scale)));
  line-height: 1.08;
}
</style>
