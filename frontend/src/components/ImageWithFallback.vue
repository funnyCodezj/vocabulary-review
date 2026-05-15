<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  src: { type: String, default: '' },
  word: { type: String, default: '?' },
})

const errored = ref(false)

const colors = ['#4f46e5', '#0891b2', '#059669', '#d97706', '#dc2626', '#7c3aed', '#db2777']
const colorIndex = computed(() => {
  let hash = 0
  for (let i = 0; i < props.word.length; i++) {
    hash = props.word.charCodeAt(i) + ((hash << 5) - hash)
  }
  return Math.abs(hash) % colors.length
})
</script>

<template>
  <div class="image-wrapper">
    <img
      v-if="src && !errored"
      :src="src"
      :alt="word"
      class="word-image"
      @error="errored = true"
    />
    <div v-else class="fallback" :style="{ background: colors[colorIndex] }">
      <span class="fallback-letter">{{ word.charAt(0).toUpperCase() }}</span>
    </div>
  </div>
</template>

<style scoped>
.image-wrapper {
  width: 100%;
  height: 100%;
}

.word-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fallback-letter {
  font-size: 48px;
  font-weight: 800;
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
