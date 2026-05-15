<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { getNextReview, submitReview, generateAudio } from '../api'
import AudioButton from '../components/AudioButton.vue'
import ImageWithFallback from '../components/ImageWithFallback.vue'

const word = ref(null)
const flipped = ref(false)
const loading = ref(true)
const submitting = ref(false)
const done = ref(false)
const count = ref(0)

async function loadNext() {
  loading.value = true
  flipped.value = false
  try {
    const res = await getNextReview()
    word.value = res.data.word
    if (!word.value.audio_path) {
      generateAudio(word.value.id).catch(() => {})
    }
  } catch {
    done.value = true
    word.value = null
  } finally {
    loading.value = false
  }
}

async function handleQuality(quality) {
  if (!word.value || submitting.value) return
  submitting.value = true
  try {
    await submitReview({
      word_id: word.value.id,
      quality,
      response_time_ms: 0,
    })
    count.value++
    loadNext()
  } catch (e) {
    console.error(e)
  } finally {
    submitting.value = false
  }
}

function reset() {
  done.value = false
  count.value = 0
  loadNext()
}

function handleKeydown(e) {
  if (!word.value || flipped.value) return
  if (e.key === ' ' || e.key === 'Enter') {
    e.preventDefault()
    flipped.value = true
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  loadNext()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <div class="flash-page">
    <div class="flash-header">
      <h1>翻卡复习</h1>
      <p class="text-secondary">空格键翻面 · 点击按钮评分</p>
    </div>

    <div v-if="done" class="done-section">
      <div class="done-card card">
        <p class="done-icon">🎉</p>
        <h2>全部完成！</h2>
        <p class="text-secondary">当前没有待复习的单词</p>
        <p class="text-sm text-secondary mt-2">本次复习 {{ count }} 个单词</p>
        <button class="btn btn-primary mt-4" @click="reset">刷新</button>
      </div>
    </div>

    <div v-else-if="loading" class="loading-section">
      <p class="text-secondary">加载中...</p>
    </div>

    <div v-else-if="word" class="flash-main">
      <div class="flash-card" :class="{ flipped: flipped }" @click="flipped = true">
        <div class="flash-front">
          <div class="flash-image">
            <ImageWithFallback :src="word.image_url" :word="word.word" />
          </div>
          <div class="flash-content">
            <h2 class="flash-word">{{ word.word }}</h2>
            <AudioButton :word="word.word" />
            <p class="text-sm text-secondary mt-2">点击或按空格翻面</p>
          </div>
        </div>
        <div class="flash-back">
          <div class="back-content">
            <p v-if="word.chinese" class="back-chinese">{{ word.chinese }}</p>
          </div>
        </div>
      </div>

      <transition name="fade">
        <div v-if="flipped" class="rating-bar">
          <p class="rating-hint">记得怎么样？</p>
          <div class="rating-buttons">
            <button class="rating-btn rating-0" @click="handleQuality(0)" :disabled="submitting">
              <span class="rating-emoji">😵</span>
              <span class="rating-label">完全忘记</span>
            </button>
            <button class="rating-btn rating-1" @click="handleQuality(1)" :disabled="submitting">
              <span class="rating-emoji">😅</span>
              <span class="rating-label">忘记了</span>
            </button>
            <button class="rating-btn rating-3" @click="handleQuality(3)" :disabled="submitting">
              <span class="rating-emoji">🤔</span>
              <span class="rating-label">有点难</span>
            </button>
            <button class="rating-btn rating-4" @click="handleQuality(4)" :disabled="submitting">
              <span class="rating-emoji">😊</span>
              <span class="rating-label">记得</span>
            </button>
            <button class="rating-btn rating-5" @click="handleQuality(5)" :disabled="submitting">
              <span class="rating-emoji">🌟</span>
              <span class="rating-label">轻松记住</span>
            </button>
          </div>
        </div>
      </transition>
    </div>

    <div class="session-count">
      本场已复习 {{ count }} 个单词
    </div>
  </div>
</template>

<style scoped>
.flash-page {
  max-width: 500px;
  margin: 0 auto;
  text-align: center;
}

.flash-header {
  margin-bottom: 24px;
}

.flash-header h1 {
  font-size: 28px;
  font-weight: 800;
  margin: 0 0 4px;
}

.flash-card {
  width: 100%;
  min-height: 400px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: transform 0.3s;
}

.flash-card:hover {
  transform: scale(1.01);
}

.flash-front, .flash-back {
  padding: 24px;
}

.flash-image {
  height: 200px;
  border-radius: var(--radius);
  overflow: hidden;
  margin-bottom: 20px;
}

.flash-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.flash-word {
  font-size: 32px;
  font-weight: 800;
  margin: 0;
}

.flash-back {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 350px;
}

.flipped .flash-front {
  display: none;
}

.flash-card:not(.flipped) .flash-back {
  display: none;
}

.back-chinese {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 8px;
}


.rating-bar {
  margin-top: 20px;
  padding: 16px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}

.rating-hint {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.rating-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}

.rating-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg-card);
  cursor: pointer;
  transition: all 0.2s;
  min-width: 70px;
}

.rating-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}
.rating-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.rating-0:hover { border-color: #ef4444; }
.rating-1:hover { border-color: #f59e0b; }
.rating-3:hover { border-color: #3b82f6; }
.rating-4:hover { border-color: #10b981; }
.rating-5:hover { border-color: #8b5cf6; }

.rating-emoji { font-size: 22px; }
.rating-label { font-size: 11px; color: var(--text-secondary); }

.done-card {
  padding: 48px 24px;
}

.done-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.loading-section {
  padding: 60px 0;
}

.session-count {
  margin-top: 16px;
  font-size: 13px;
  color: var(--text-secondary);
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
