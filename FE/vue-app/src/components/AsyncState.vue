<template>
  <div class="async-state">
    <div v-if="isLoading" class="state-loading" role="status" aria-live="polite">
      <slot name="loading">
        <SkeletonBox v-for="n in skeletonLines" :key="n" :height="n === 1 ? '28px' : '16px'" :width="n === 1 ? '60%' : '100%'" />
        <p class="sr-only">Loading…</p>
      </slot>
    </div>

    <div v-else-if="error" class="state-error" role="alert">
      <slot name="error" :error="error" :retry="retry">
        <div class="error-card">
          <span class="error-icon" aria-hidden="true">⚠</span>
          <div class="error-body">
            <p class="error-title">{{ errorTitle }}</p>
            <p class="error-msg">{{ error.message }}</p>
            <button
              v-if="error.retryable && retry"
              class="error-retry"
              type="button"
              @click="retry"
            >
              Try again
            </button>
          </div>
        </div>
      </slot>
    </div>

    <div v-else-if="isEmpty" class="state-empty">
      <slot name="empty">
        <p class="empty-msg">No information to show here yet.</p>
      </slot>
    </div>

    <div v-else class="state-content">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import SkeletonBox from './SkeletonBox.vue'

const props = defineProps({
  isLoading:     { type: Boolean, default: false },
  error:         { type: Object,  default: null },
  isEmpty:       { type: Boolean, default: false },
  retry:         { type: Function, default: null },
  skeletonLines: { type: Number,  default: 4 },
})

const errorTitle = computed(() => {
  if (!props.error) return ''
  if (props.error.kind === 'http' && props.error.status === 404) return 'Not found'
  if (props.error.kind === 'http' && props.error.status === 503) return 'Just a moment'
  if (props.error.kind === 'timeout')                            return 'Taking longer than usual'
  if (props.error.kind === 'network')                            return 'Connection trouble'
  return 'Something went wrong'
})
</script>

<style scoped>
.async-state { width: 100%; }

.state-loading { display: flex; flex-direction: column; gap: 10px; }

.error-card {
  display: flex;
  gap: 14px;
  padding: 16px 18px;
  background: #FEF5E7;
  border: 1px solid #F3D7A8;
  border-radius: 12px;
  align-items: flex-start;
}
.error-icon {
  font-size: 22px;
  color: #B07919;
  line-height: 1;
  flex-shrink: 0;
}
.error-body { flex: 1; min-width: 0; }
.error-title {
  font-family: Georgia, serif;
  margin: 0 0 4px;
  font-size: calc(17px * var(--font-scale));
  color: #4A2E10;
  font-weight: 700;
}
.error-msg {
  margin: 0 0 12px;
  font-size: calc(14px * var(--font-scale));
  line-height: 1.6;
  color: #4A2E10;
}
.error-retry {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  background: transparent;
  border: 1.5px solid #B07919;
  border-radius: 999px;
  color: #4A2E10;
  font-size: calc(13px * var(--font-scale));
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.error-retry:hover {
  background: #B07919;
  color: white;
}

.state-empty {
  padding: 24px 16px;
  text-align: center;
  color: #6a8e6e;
  font-size: calc(14px * var(--font-scale));
}

.sr-only {
  position: absolute;
  width: 1px; height: 1px;
  padding: 0; margin: -1px;
  overflow: hidden;
  clip: rect(0,0,0,0);
  white-space: nowrap;
  border: 0;
}
</style>
