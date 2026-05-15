<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getWord, deleteWord, fetchWordDict, generateAudio, fetchImage, clearErrorWord } from '../api'
import AudioButton from '../components/AudioButton.vue'
import ImageWithFallback from '../components/ImageWithFallback.vue'

const route = useRoute()
const router = useRouter()
const word = ref(null)
const loading = ref(true)
const loadingDict = ref(false)
const loadingAudio = ref(false)
const loadingImage = ref(false)
const isFromErrors = computed(() => route.query.from === 'errors')

async function loadWord() {
  loading.value = true
  try {
    const res = await getWord(route.params.id)
    word.value = res.data
  } catch (e) {
    router.push(isFromErrors.value ? '/review/errors' : '/words')
  } finally {
    loading.value = false
  }
}

async function loadDictionary() {
  loadingDict.value = true
  try {
    await fetchWordDict(word.value.id)
    await loadWord()
  } catch (e) {
    alert('未找到词典数据')
  } finally {
    loadingDict.value = false
  }
}

async function loadAudio() {
  loadingAudio.value = true
  try {
    await generateAudio(word.value.id)
    await loadWord()
  } finally {
    loadingAudio.value = false
  }
}

async function loadImage() {
  loadingImage.value = true
  try {
    await fetchImage(word.value.id)
    await loadWord()
  } finally {
    loadingImage.value = false
  }
}

async function handleDelete() {
  if (isFromErrors.value) {
    if (!confirm(`将「${word.value.word}」移出错题集？`)) return
    try {
      await clearErrorWord(word.value.id)
      router.push('/review/errors')
    } catch {
      alert('操作失败')
    }
    return
  }
  if (!confirm(`确定删除单词「${word.value.word}」？此操作不可恢复。`)) return
  try {
    await deleteWord(word.value.id)
    router.push('/words')
  } catch {
    alert('删除失败')
  }
}

function stageLabel(stage) {
  const labels = ['新词', '学习中', '复习中', '复习中', '已掌握', '已精通']
  return labels[stage] || '新词'
}

onMounted(loadWord)
</script>

<template>
  <div v-if="loading" class="loading-page">
    <p class="text-secondary">加载中...</p>
  </div>

  <div v-else-if="word" class="detail-page">
    <div class="detail-top-bar">
      <button class="btn btn-outline" @click="router.push(isFromErrors ? '/review/errors' : '/words')">
        ← 返回
      </button>
      <button class="btn btn-outline" :class="isFromErrors ? 'btn-clear' : 'btn-delete'" @click="handleDelete">
        {{ isFromErrors ? '清除错题记录' : '删除单词' }}
      </button>
    </div>

    <div class="detail-layout">
      <div class="image-section">
        <div class="image-card">
          <ImageWithFallback :src="word.image_url" :word="word.word" />
        </div>
        <button
          class="btn btn-outline mt-2"
          @click="loadImage"
          :disabled="loadingImage"
        >
          {{ loadingImage ? '获取中...' : (word.image_url ? '刷新图片' : '获取图片') }}
        </button>
      </div>

      <div class="info-section">
        <div class="word-header">
          <h1 class="word-title">{{ word.word }}</h1>
          <AudioButton :word="word.word" />
        </div>

        <p class="phonetic">{{ word.phonetic || '暂无音标' }}</p>

        <div class="stage-indicator">
          <span class="stage-dot" :class="`dot-${word.stage}`"></span>
          <span>{{ stageLabel(word.stage) }}</span>
          <span v-if="word.next_review_date" class="text-sm text-secondary">
            — 下次复习: {{ word.next_review_date }}
          </span>
        </div>

        <div class="section-card">
          <h3>释义</h3>
          <p v-if="word.chinese" class="chinese-text">{{ word.chinese }}</p>
          <p v-if="word.definition">{{ word.definition }}</p>
          <p v-else-if="!word.chinese" class="text-secondary">尚未加载</p>
          <button
            v-if="!word.definition"
            class="btn btn-outline mt-2"
            @click="loadDictionary"
            :disabled="loadingDict"
          >
            {{ loadingDict ? '加载中...' : '加载词典数据' }}
          </button>
        </div>

        <div v-if="word.example" class="section-card">
          <h3>例句</h3>
          <p class="example-text">"{{ word.example }}"</p>
        </div>

        <div class="section-card stats-card">
          <h3>学习统计</h3>
          <div class="progress-stats">
            <div class="pstat">
              <span class="pstat-value">{{ word.correct_count }}</span>
              <span class="pstat-label">正确</span>
            </div>
            <div class="pstat">
              <span class="pstat-value">{{ word.incorrect_count }}</span>
              <span class="pstat-label">错误</span>
            </div>
            <div class="pstat">
              <span class="pstat-value">{{ word.repetition }}</span>
              <span class="pstat-label">连续正确</span>
            </div>
            <div class="pstat">
              <span class="pstat-value">{{ word.ease_factor }}</span>
              <span class="pstat-label">难度系数</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.loading-page {
  text-align: center;
  padding: 60px 0;
}

.detail-top-bar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.btn-delete {
  color: var(--error);
  border-color: var(--error);
}
.btn-delete:hover {
  background: var(--error);
  color: white;
}

.btn-clear {
  color: var(--primary);
  border-color: var(--primary);
}
.btn-clear:hover {
  background: var(--primary);
  color: white;
}

.detail-layout {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 24px;
}

.image-section {
  display: flex;
  flex-direction: column;
}

.image-card {
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--border);
  height: 300px;
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.word-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.word-title {
  font-size: 36px;
  font-weight: 800;
  margin: 0;
}

.phonetic {
  font-size: 16px;
  color: var(--text-secondary);
  font-style: italic;
}

.stage-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.stage-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot-0 { background: #94a3b8; }
.dot-1 { background: #f59e0b; }
.dot-2 { background: #3b82f6; }
.dot-3 { background: #10b981; }
.dot-4 { background: #10b981; }
.dot-5 { background: #8b5cf6; }

.section-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
}

.section-card h3 {
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.example-text {
  font-style: italic;
  color: var(--text);
}

.chinese-text {
  font-size: 18px;
  font-weight: 600;
  color: var(--primary);
  margin-bottom: 8px;
}

.progress-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  text-align: center;
}

.pstat-value {
  display: block;
  font-size: 22px;
  font-weight: 700;
}

.pstat-label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
}

@media (max-width: 640px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }
  .image-card {
    height: 200px;
  }
}
</style>
