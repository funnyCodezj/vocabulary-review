<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { getNextReview, submitReview, listWords, generateAudio, getStats } from '../api'
import AudioButton from '../components/AudioButton.vue'

const word = ref(null)
const options = ref([])
const selected = ref(null)
const answered = ref(false)
const isCorrect = ref(false)
const loading = ref(true)
const submitting = ref(false)
const done = ref(false)
const score = ref({ correct: 0, total: 0 })
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
  score.value = { correct: 0, total: 0 }
  loadNext()
}

const confettiColors = ['#4f46e5', '#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#ec4899', '#8b5cf6']
function confettiStyle(i) {
  const color = confettiColors[i % confettiColors.length]
  return {
    left: `${Math.random() * 100}%`,
    background: color,
    animationDelay: `${Math.random() * 0.5}s`,
    animationDuration: `${0.8 + Math.random() * 0.6}s`,
  }
}

async function loadNext() {
  loading.value = true
  selected.value = null
  answered.value = false
  try {
    // get the target word from review queue
    const reviewRes = await getNextReview(stageFilter.value)
    const target = reviewRes.data.word
    word.value = target

    // fetch audio in background if missing
    if (!target.audio_path) {
      generateAudio(target.id).catch(() => {})
    }

    // fetch distractors from word list
    const allRes = await listWords({ page_size: 100 })
    const others = allRes.data.items.filter(w => w.id !== target.id && (w.chinese || w.definition))
    const shuffled = others.sort(() => Math.random() - 0.5).slice(0, 3)

    // combine correct + distractors and shuffle
    const allOptions = [
      { text: target.chinese || target.definition || `${target.word}: loading...`, correct: true },
      ...shuffled.map(w => ({ text: w.chinese || w.definition, correct: false })),
    ]
    options.value = allOptions.sort(() => Math.random() - 0.5)
  } catch {
    done.value = true
    word.value = null
  } finally {
    loading.value = false
  }
}

function selectOption(opt) {
  if (answered.value || submitting.value) return
  selected.value = opt
  answered.value = true
  isCorrect.value = opt.correct
  score.value.total++
  if (opt.correct) {
    score.value.correct++
    playCorrectSound()
  }
}

async function next() {
  if (word.value && answered.value) {
    submitting.value = true
    try {
      await submitReview({
        word_id: word.value.id,
        quality: isCorrect.value ? 4 : 1,
        response_time_ms: 0,
      })
    } catch (e) {
      console.error(e)
    } finally {
      submitting.value = false
    }
  }
  loadNext()
}

function backToMode() {
  modeSelected.value = false
  done.value = false
  word.value = null
  score.value = { correct: 0, total: 0 }
}

function reset() {
  done.value = false
  score.value = { correct: 0, total: 0 }
  selectMode(stageFilter.value)
}

function playCorrectSound() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)()
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()
    osc.connect(gain)
    gain.connect(ctx.destination)
    osc.type = 'sine'
    osc.frequency.setValueAtTime(523, ctx.currentTime)
    osc.frequency.setValueAtTime(659, ctx.currentTime + 0.1)
    osc.frequency.setValueAtTime(784, ctx.currentTime + 0.2)
    gain.gain.setValueAtTime(0.25, ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5)
    osc.start(ctx.currentTime)
    osc.stop(ctx.currentTime + 0.5)
  } catch {}
}

function handleKeydown(e) {
  if (e.key === ' ' || e.code === 'Space') {
    e.preventDefault()
    if (answered.value && !submitting.value) {
      next()
    }
  }
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
  <div class="quiz-page">
    <div class="quiz-header">
      <h1>选择题测验</h1>
      <div class="score-display" v-if="score.total > 0">
        <span class="score-correct">{{ score.correct }}</span>
        <span class="score-sep">/</span>
        <span class="score-total">{{ score.total }}</span>
        <span class="score-pct">({{ Math.round(score.correct / score.total * 100) }}%)</span>
      </div>
    </div>

    <div v-if="!modeSelected" class="mode-select-section">
      <h2 class="mode-title">请选择测验范围</h2>
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
        <p class="quiz-final-score mt-2">
          Final: {{ score.correct }}/{{ score.total }} ({{ Math.round(score.correct / score.total * 100) || 0 }}%)
        </p>
        <button v-if="modeCounts[stageFilter] > 0" class="btn btn-primary" @click="reset">再来一次</button>
        <button class="btn-ghost" @click="backToMode">切换范围</button>
      </div>
    </div>

    <div v-else-if="loading" class="loading-section">
      <div class="loader-dots">
        <span></span><span></span><span></span>
      </div>
      <p class="text-secondary mt-2">加载下一题...</p>
    </div>

    <div v-else-if="word" class="quiz-main">
      <div class="question-card card">
        <div class="question-word">
          <h2 class="word-text">{{ word.word }}</h2>
          <AudioButton :word="word.word" />
        </div>
        <p class="question-hint">选择正确的释义</p>
      </div>

      <div class="options-list">
        <button
          v-for="(opt, i) in options"
          :key="i"
          class="option-btn"
          :class="{
            correct: answered && opt.correct,
            incorrect: answered && selected === opt && !opt.correct,
            disabled: answered && selected !== opt && !opt.correct,
          }"
          @click="selectOption(opt)"
          :disabled="answered"
        >
          <span class="option-letter">{{ 'ABCD'[i] }}</span>
          <span class="option-text">{{ opt.text }}</span>
          <span v-if="answered && opt.correct" class="option-icon">✓</span>
          <span v-if="answered && selected === opt && !opt.correct" class="option-icon">✗</span>
        </button>
      </div>

      <transition name="fade">
        <div v-if="answered" class="feedback-bar" :class="{ correct: isCorrect, incorrect: !isCorrect }">
          <p>{{ isCorrect ? '回答正确！🎉' : '再想想！😅' }}</p>
          <button class="btn btn-primary" @click="next" :disabled="submitting">
            {{ submitting ? '保存中...' : '下一题 →' }}
          </button>
        </div>
      </transition>
    </div>

    <div v-if="modeSelected" class="session-count">
      <span>范围：{{ modeOptions.find(o => o.value === stageFilter)?.label }} · 共 {{ modeCounts[stageFilter] ?? '?' }} 个 · 本场 {{ score.total }} 个</span>
      <button class="switch-mode-btn" @click="backToMode">切换范围</button>
    </div>
  </div>
</template>

<style scoped>
.quiz-page {
  max-width: 600px;
  margin: 0 auto;
}

.quiz-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.quiz-header h1 {
  font-size: 28px;
  font-weight: 800;
  margin: 0;
}

/* ===== Mode Selection (shared classes with flash) ===== */
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

.score-display {
  font-size: 16px;
  font-weight: 600;
}

.score-correct { color: var(--success); }
.score-sep { color: var(--text-secondary); }
.score-total { color: var(--text); }
.score-pct { color: var(--text-secondary); font-size: 14px; }

.question-card {
  padding: 32px 24px;
  text-align: center;
  margin-bottom: 20px;
}

.question-word {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 12px;
}

.word-text {
  font-size: 36px;
  font-weight: 800;
  margin: 0;
}

.question-hint {
  color: var(--text-secondary);
  font-size: 14px;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option-btn {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg-card);
  cursor: pointer;
  text-align: left;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 15px;
  position: relative;
}

.option-btn:not(.disabled):hover {
  border-color: var(--primary);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.12);
  transform: translateX(4px);
}

.option-btn.correct {
  border-color: var(--success);
  background: #f0fdf4;
  animation: pulseCorrect 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.option-btn.incorrect {
  border-color: var(--error);
  background: #fef2f2;
  animation: shakeWrong 0.5s cubic-bezier(0.36, 0.07, 0.19, 0.97);
}

.option-letter {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--bg);
  font-weight: 700;
  font-size: 13px;
  flex-shrink: 0;
}

.option-text {
  flex: 1;
  line-height: 1.4;
}

.option-icon {
  font-size: 18px;
  font-weight: 700;
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
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.switch-mode-btn {
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

.switch-mode-btn:hover {
  border-color: var(--primary-light);
  color: var(--primary);
}

.option-btn.correct {
  border-color: var(--success);
  background: #f0fdf4;
}
.option-btn.correct .option-letter {
  background: var(--success);
  color: white;
}

.option-btn.incorrect {
  border-color: var(--error);
  background: #fef2f2;
}
.option-btn.incorrect .option-letter {
  background: var(--error);
  color: white;
}

.option-btn.disabled {
  opacity: 0.5;
  cursor: default;
}

.feedback-bar {
  margin-top: 20px;
  padding: 16px 20px;
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.feedback-bar.correct {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
}

.feedback-bar.incorrect {
  background: #fef2f2;
  border: 1px solid #fecaca;
}

.done-card {
  padding: 48px 24px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.done-card h2, .done-card p, .done-card button {
  position: relative;
  z-index: 1;
}

.done-icon {
  font-size: 48px;
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
}

.quiz-final-score {
  font-size: 18px;
  font-weight: 700;
}

.loading-section {
  text-align: center;
  padding: 60px 0;
}

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

@keyframes shakeWrong {
}

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

@keyframes shakeWrong {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

@keyframes pulseCorrect {
  0% { transform: scale(1); }
  50% { transform: scale(1.03); }
  100% { transform: scale(1); }
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

@keyframes dotBounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

@media (max-width: 640px) {
  .mode-grid {
    grid-template-columns: 1fr;
  }
}
</style>
