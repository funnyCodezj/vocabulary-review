<script setup>
import { ref } from 'vue'

const props = defineProps({
  word: { type: String, required: true },
})

const playing = ref(false)

function play() {
  if (playing.value) return
  playing.value = true
  const utterance = new SpeechSynthesisUtterance(props.word)
  utterance.lang = 'en-US'
  utterance.rate = 0.9
  utterance.onend = () => { playing.value = false }
  utterance.onerror = () => { playing.value = false }
  speechSynthesis.speak(utterance)
}
</script>

<template>
  <button class="audio-btn" @click.stop="play" :title="`Play '${word}'`">
    <svg :class="{ spinning: playing }" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
      <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
      <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
    </svg>
  </button>
</template>

<style scoped>
.audio-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid var(--border);
  border-radius: 50%;
  background: var(--bg);
  color: var(--primary);
  cursor: pointer;
  transition: all 0.2s;
}

.audio-btn:hover {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.spinning {
  animation: pulse 0.6s ease-in-out infinite alternate;
}

@keyframes pulse {
  from { transform: scale(1); }
  to { transform: scale(1.15); }
}
</style>
