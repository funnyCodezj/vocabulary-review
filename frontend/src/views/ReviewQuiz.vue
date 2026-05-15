<script setup>
import { ref, onMounted, computed } from 'vue'
import { getNextReview, submitReview, listWords, generateAudio } from '../api'
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

async function loadNext() {
  loading.value = true
  selected.value = null
  answered.value = false
  try {
    // get the target word from review queue
    const reviewRes = await getNextReview()
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
  if (opt.correct) score.value.correct++
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

function reset() {
  done.value = false
  score.value = { correct: 0, total: 0 }
  loadNext()
}

onMounted(loadNext)
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

    <div v-if="done" class="done-section">
      <div class="done-card card">
        <p class="done-icon">🎉</p>
        <h2>全部完成！</h2>
        <p class="text-secondary">当前没有待复习的单词</p>
        <p class="quiz-final-score mt-2">
          Final: {{ score.correct }}/{{ score.total }} ({{ Math.round(score.correct / score.total * 100) || 0 }}%)
        </p>
        <button class="btn btn-primary mt-4" @click="reset">重新开始</button>
      </div>
    </div>

    <div v-else-if="loading" class="loading-section">
      <p class="text-secondary">加载下一题...</p>
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
  transition: all 0.2s;
  font-size: 15px;
}

.option-btn:not(.disabled):hover {
  border-color: var(--primary);
  box-shadow: var(--shadow);
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
}

.done-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.quiz-final-score {
  font-size: 18px;
  font-weight: 700;
}

.loading-section {
  text-align: center;
  padding: 60px 0;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
