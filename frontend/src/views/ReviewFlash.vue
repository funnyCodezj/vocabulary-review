<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { getNextReview, submitReview, generateAudio, getStats } from '../api'
import AudioButton from '../components/AudioButton.vue'
import ImageWithFallback from '../components/ImageWithFallback.vue'

const word = ref(null)
const flipped = ref(false)
const loading = ref(true)
const submitting = ref(false)
const done = ref(false)
const count = ref(0)
const stageFilter = ref('due')
const modeSelected = ref(false)
const modeCounts = ref({})

const modeOptions = [
  { value: 'due', label: '待复习', desc: '到期需复习的单词' },
  { value: 'all', label: '全部单词', desc: '所有单词按顺序出现' },
  { value: 'new', label: '新词', desc: '从未复习或已重置的单词' },
  { value: 'learning', label: '学习中', desc: '刚答对过 1 次，间隔 1 天' },
  { value: 'reviewing', label: '复习中', desc: '间隔 6~21 天，逐渐巩固' },
  { value: 'mastered', label: '已掌握', desc: '间隔超过 21 天，基本记住' },
  { value: 'errors', label: '错题', desc: '曾经答错的单词' },
]

function selectMode(value) {
  stageFilter.value = value
  modeSelected.value = true
  count.value = 0
  loadNext()
}

const confettiColors = ['#4f46e5', '#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#ec4899', '#8b5cf6']
function confettiStyle(i) {
  const color = confettiColors[i % confettiColors.length]
  const left = Math.random() * 100
  const delay = Math.random() * 0.5
  const duration = 0.8 + Math.random() * 0.6
  return {
    left: `${left}%`,
    background: color,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`,
  }
}

async function loadNext() {
  loading.value = true
  flipped.value = false
  try {
    const res = await getNextReview(stageFilter.value)
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
  if (quality >= 4) playSuccessSound()
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

function backToMode() {
  modeSelected.value = false
  done.value = false
  word.value = null
  count.value = 0
}

function reset() {
  done.value = false
  count.value = 0
  selectMode(stageFilter.value)
}

function handleKeydown(e) {
  if (!word.value || submitting.value) return
  if (e.key === ' ' || e.key === 'Enter') {
    e.preventDefault()
    if (flipped.value) {
      handleQuality(4) // 默认"记得"
    } else {
      flipped.value = true
    }
  }
}

function playSuccessSound() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)()
    const now = ctx.currentTime
    // C5 → E5 → G5 上行和弦
    const freqs = [523.25, 659.25, 783.99]
    freqs.forEach((freq, i) => {
      const osc = ctx.createOscillator()
      const gain = ctx.createGain()
      osc.type = 'sine'
      osc.frequency.value = freq
      gain.gain.setValueAtTime(0, now + i * 0.08)
      gain.gain.linearRampToValueAtTime(0.15, now + i * 0.08 + 0.04)
      gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.08 + 0.4)
      osc.connect(gain)
      gain.connect(ctx.destination)
      osc.start(now + i * 0.08)
      osc.stop(now + i * 0.08 + 0.4)
    })
  } catch {}
}

onMounted(async () => {
  window.addEventListener('keydown', handleKeydown)
  loading.value = false  // wait for mode selection
  try {
    const res = await getStats()
    const s = res.data
    modeCounts.value = {
      due: s.due_count,
      all: s.total_words,
      new: s.stage_0_new,
      learning: s.stage_1_learning,
      reviewing: s.stage_2_3_reviewing,
      mastered: s.stage_4_5_known,
      errors: s.errors_count,
    }
  } catch {}
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <div class="flash-page">
    <div class="flash-header">
      <h1>翻卡复习</h1>
      <p v-if="modeSelected" class="text-secondary">
        <kbd>空格键</kbd> 翻面 · 再按 <kbd>空格键</kbd> 默认「记得」
      </p>
    </div>

    <div v-if="!modeSelected" class="mode-select-section">
      <h2 class="mode-title">请选择复习范围</h2>
      <div class="mode-grid">
        <button
          v-for="opt in modeOptions"
          :key="opt.value"
          class="mode-btn"
          @click="selectMode(opt.value)"
        >
          <span class="mode-label">{{ opt.label }}</span>
          <span class="mode-desc">{{ opt.desc }}</span>
          <span class="mode-count">{{ modeCounts[opt.value] ?? '...' }} 个</span>
        </button>
      </div>
    </div>

    <div v-else-if="done" class="done-section">
      <div class="done-card card">
        <div class="confetti-container">
          <div v-for="i in 20" :key="i" class="confetti-piece" :style="confettiStyle(i)"></div>
        </div>
        <p class="done-icon">🎉</p>
        <h2>全部完成！</h2>
        <p class="text-secondary">当前没有待复习的单词</p>
        <p class="text-sm text-secondary mt-2">本次复习 {{ count }} 个单词</p>
        <button v-if="modeCounts[stageFilter] > 0" class="btn btn-primary" @click="reset">再来一次</button>
        <button class="btn-ghost" @click="backToMode">切换范围</button>
      </div>
    </div>

    <div v-else-if="loading" class="loading-section">
      <div class="loader-dots">
        <span></span><span></span><span></span>
      </div>
      <p class="text-secondary mt-2">加载中...</p>
    </div>

    <div v-else-if="word" class="flash-main">
      <div class="flash-card" :class="{ flipped: flipped }" @click="flipped = true">
        <div class="flash-card-inner">
          <div class="flash-front">
            <div class="flash-image">
              <ImageWithFallback :src="word.image_url" :word="word.word" />
            </div>
            <div class="flash-content">
              <h2 class="flash-word">{{ word.word }}</h2>
              <AudioButton :word="word.word" />
              <p v-if="!flipped" class="text-sm text-secondary mt-2">点击或按空格翻面</p>
            </div>
          </div>
          <div class="flash-back">
            <div class="back-content">
              <p v-if="word.chinese" class="back-chinese">{{ word.chinese }}</p>
            </div>
          </div>
        </div>
      </div>

      <Transition name="sidebar">
        <div v-if="flipped" class="rating-bar">
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
      </Transition>
    </div>

    <div v-if="modeSelected" class="session-count">
      <span>范围：{{ modeOptions.find(o => o.value === stageFilter)?.label }} · 共 {{ modeCounts[stageFilter] ?? '?' }} 个 · 本场 {{ count }} 个</span>
      <button class="btn-switch-mode" @click="backToMode">切换范围</button>
    </div>
  </div>
</template>

<style scoped>
.flash-page {
  max-width: 700px;
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

.flash-header kbd {
  display: inline-block;
  padding: 2px 6px;
  font-size: 12px;
  font-family: inherit;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 4px;
  box-shadow: 0 1px 0 var(--border);
}

/* ===== Side-by-side layout ===== */
.flash-main {
  display: flex;
  justify-content: center;
  align-items: stretch;
  gap: 16px;
}

/* ===== 3D Card Flip ===== */
.flash-card {
  flex: 0 1 520px;
  perspective: 1000px;
  cursor: pointer;
  min-height: 420px;
}

.flash-card-inner {
  position: relative;
  width: 100%;
  min-height: 420px;
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  transform-style: preserve-3d;
}

.flipped .flash-card-inner {
  transform: rotateY(180deg);
}

.flash-front, .flash-back {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.flash-image {
  height: 200px;
  border-radius: var(--radius);
  overflow: hidden;
  margin-bottom: 20px;
  flex-shrink: 0;
}

.flash-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.flash-word {
  font-size: 36px;
  font-weight: 800;
  margin: 0;
}

.flash-back {
  transform: rotateY(180deg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-content {
  width: 100%;
}

.back-chinese {
  font-size: 26px;
  font-weight: 700;
  color: var(--primary);
}

/* ===== Rating Bar (vertical sidebar) ===== */
.rating-bar {
  width: 130px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  padding: 12px 10px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
}

.rating-buttons {
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 6px;
}

.rating-btn {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg-card);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  text-align: left;
  width: 100%;
  min-height: 44px;
}

/* ===== Sidebar enter/leave transition ===== */
.sidebar-enter-active {
  animation: sidebarIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.sidebar-leave-active {
  animation: sidebarIn 0.2s ease reverse;
}

@keyframes sidebarIn {
  from { opacity: 0; transform: translateX(16px); }
  to { opacity: 1; transform: translateX(0); }
}

.rating-btn:hover {
  transform: translateX(4px) scale(1.03);
  box-shadow: var(--shadow);
}

.rating-btn:active {
  transform: translateX(2px) scale(0.98);
}

.rating-btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none !important; }

.rating-0:hover { border-color: #ef4444; background: #fef2f2; }
.rating-1:hover { border-color: #f59e0b; background: #fffbeb; }
.rating-3:hover { border-color: #3b82f6; background: #eff6ff; }
.rating-4:hover { border-color: #10b981; background: #f0fdf4; }
.rating-5:hover { border-color: #8b5cf6; background: #faf5ff; }

.rating-emoji { font-size: 18px; flex-shrink: 0; }
.rating-label { font-size: 12px; color: var(--text-secondary); font-weight: 500; line-height: 1.2; }

/* ===== Done / Completion ===== */
.done-card {
  padding: 48px 24px;
  position: relative;
  overflow: hidden;
}

.done-icon {
  font-size: 48px;
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
}

.done-card h2 {
  position: relative;
  z-index: 1;
}

.done-card .text-secondary {
  position: relative;
  z-index: 1;
}

.done-card .btn {
  position: relative;
  z-index: 1;
}

/* ===== Confetti Effect ===== */
.confetti-container {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.confetti-piece {
  position: absolute;
  top: -10px;
  width: 8px;
  height: 8px;
  border-radius: 2px;
  animation: confettiFall ease-out forwards;
}

@keyframes confettiFall {
  0% {
    transform: translateY(0) rotate(0deg) scale(1);
    opacity: 1;
  }
  100% {
    transform: translateY(350px) rotate(720deg) scale(0.3);
    opacity: 0;
  }
}

/* ===== Loading Dots ===== */
.loader-dots {
  display: flex;
  justify-content: center;
  gap: 8px;
  padding: 40px 0 0;
}

.loader-dots span {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--primary);
  animation: dotBounce 1.4s ease-in-out infinite both;
}

.loader-dots span:nth-child(1) { animation-delay: -0.32s; background: var(--primary); }
.loader-dots span:nth-child(2) { animation-delay: -0.16s; background: var(--primary-light); }
.loader-dots span:nth-child(3) { animation-delay: 0s; background: var(--primary); }

@keyframes dotBounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.loading-section {
  padding: 20px 0 60px;
}

/* ===== Mode Selection ===== */
.mode-select-section {
  padding: 20px 0;
}

.mode-title {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 20px;
  text-align: center;
}

.mode-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  max-width: 500px;
  margin: 0 auto;
}

.mode-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 20px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  font-family: inherit;
}

.mode-btn:hover {
  border-color: var(--primary-light);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.12);
  transform: translateY(-2px);
}

.mode-btn:active {
  transform: translateY(0) scale(0.98);
}

.mode-label {
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
}

.mode-desc {
  font-size: 12px;
  color: var(--text-secondary);
  text-align: center;
  line-height: 1.4;
}

.mode-count {
  font-size: 13px;
  font-weight: 700;
  color: var(--primary);
  margin-top: 4px;
}

.btn-ghost {
  display: block;
  width: fit-content;
  margin: 12px auto 0;
  padding: 8px 16px;
  border: none;
  border-radius: var(--radius);
  background: transparent;
  color: var(--text-secondary);
  font-size: 14px;
  font-family: inherit;
  cursor: pointer;
  transition: color 0.2s;
}

.btn-ghost:hover {
  color: var(--primary);
}

.session-count {
  margin-top: 16px;
  font-size: 13px;
  color: var(--text-secondary);
  animation: fadeIn 0.6s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.btn-switch-mode {
  font-size: 12px;
  padding: 4px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s ease;
}

.btn-switch-mode:hover {
  border-color: var(--primary-light);
  color: var(--primary);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* ===== Mobile: stack vertically ===== */
@media (max-width: 640px) {
  .flash-page {
    max-width: 500px;
  }

  .flash-main {
    flex-direction: column;
    align-items: center;
  }

  .flash-card {
    width: 100%;
    min-height: 360px;
  }

  .flash-card-inner {
    min-height: 360px;
  }

  .flash-front, .flash-back {
    padding: 20px 16px;
  }

  .flash-word {
    font-size: 28px;
  }

  .back-chinese {
    font-size: 20px;
  }

  .flash-image {
    height: 160px;
  }

  .mode-grid {
    grid-template-columns: 1fr;
  }

  .rating-bar {
    width: 100%;
    flex-direction: row;
    padding: 10px 12px;
  }

  .rating-buttons {
    flex-direction: row;
    flex: initial;
    width: 100%;
    justify-content: center;
    gap: 6px;
  }

  .rating-btn {
    flex: 1;
    flex-direction: column;
    padding: 8px 6px;
    min-width: 0;
    text-align: center;
    gap: 2px;
    min-height: 56px;
  }

  .rating-btn:hover {
    transform: translateY(-2px) scale(1.05);
  }

  .rating-emoji { font-size: 20px; }
  .rating-label { font-size: 10px; }
}
</style>
