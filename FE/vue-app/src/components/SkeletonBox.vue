<template>
  <div
    class="skeleton-box"
    :style="{ width, height }"
    aria-hidden="true"
  ></div>
</template>

<script setup>
defineProps({
  width:  { type: String, default: '100%' },
  height: { type: String, default: '16px' },
})
</script>

<style scoped>
.skeleton-box {
  display: block;
  border-radius: 6px;
  background: linear-gradient(
    90deg,
    rgba(29, 113, 105, 0.07) 0%,
    rgba(29, 113, 105, 0.14) 50%,
    rgba(29, 113, 105, 0.07) 100%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.4s ease-in-out infinite;
}

@keyframes skeleton-shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

@media (prefers-reduced-motion: reduce) {
  .skeleton-box {
    animation: none;
    background: rgba(29, 113, 105, 0.1);
  }
}
</style>
