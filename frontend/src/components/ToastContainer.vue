<script setup>
import { useToast } from '../composables/useToast'

const { toasts, dismiss } = useToast()

const iconMap = { info: 'ℹ️', success: '✅', error: '❌' }
</script>

<template>
  <div class="toast-container">
    <TransitionGroup name="toast">
      <div
        v-for="t in toasts"
        :key="t.id"
        class="toast"
        :class="'toast-' + t.type"
      >
        <span class="toast-icon">{{ iconMap[t.type] || 'ℹ️' }}</span>
        <span class="toast-text">{{ t.message }}</span>
        <button class="toast-close" @click="dismiss(t.id)">✕</button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  font-size: 14px;
  line-height: 1.5;
  max-width: 420px;
  pointer-events: auto;
}

.toast-info {
  background: #1e293b;
  color: #e2e8f0;
}

.toast-success {
  background: #065f46;
  color: #d1fae5;
}

.toast-error {
  background: #991b1b;
  color: #fee2e2;
}

.toast-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.toast-text {
  flex: 1;
}

.toast-close {
  background: none;
  border: none;
  color: inherit;
  opacity: 0.6;
  cursor: pointer;
  font-size: 14px;
  padding: 2px 6px;
  border-radius: 4px;
  flex-shrink: 0;
  font-family: inherit;
}

.toast-close:hover {
  opacity: 1;
  background: rgba(255,255,255,0.1);
}

.toast-enter-active {
  animation: toastIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.toast-leave-active {
  animation: toastIn 0.2s ease reverse;
}

@keyframes toastIn {
  from { opacity: 0; transform: translateX(100%); }
  to { opacity: 1; transform: translateX(0); }
}
</style>
