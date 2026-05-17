<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getWord, deleteWord, fetchWordDict, generateAudio, fetchImage, clearImage, clearErrorWord } from '../api'
import { ArrowLeft, Trash2 } from 'lucide-vue-next'
import AudioButton from '../components/AudioButton.vue'
import ImageWithFallback from '../components/ImageWithFallback.vue'

const route = useRoute()
const router = useRouter()
const word = ref(null)
const loading = ref(true)
const loadingDict = ref(false)
const loadingAudio = ref(false)
const loadingImage = ref(false)
const deletingImage = ref(false)
const hoverImage = ref(false)
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

async function handleClearImage() {
  if (!confirm('删除此图片？')) return
  deletingImage.value = true
  try {
    await clearImage(word.value.id)
    await loadWord()
  } catch {
    alert('删除失败')
  } finally {
    deletingImage.value = false
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

function shortPos(pos) {
  const map = { noun: 'n.', verb: 'v.', adjective: 'adj.', adverb: 'adv.', pronoun: 'pron.',
    preposition: 'prep.', conjunction: 'conj.', interjection: 'interj.', numeral: 'num.', article: 'art.' }
  return map[pos] || pos
}

const hasDictionaryData = computed(() => {
  return word.value?.meanings?.length > 0
})

onMounted(loadWord)
</script>

<template>
  <div v-if="loading" class="loading-page">
    <p class="text-secondary">加载中...</p>
  </div>

  <div v-else-if="word" class="detail-page">
    <div class="detail-top-bar">
      <button class="btn btn-outline" @click="router.push(isFromErrors ? '/review/errors' : '/words')">
        <ArrowLeft :size="16" stroke-width="1.5" />
        返回
      </button>
      <button class="btn btn-outline" :class="isFromErrors ? 'btn-clear' : 'btn-delete'" @click="handleDelete">
        {{ isFromErrors ? '清除错题记录' : '删除单词' }}
      </button>
    </div>

    <div class="detail-layout">
      <div class="image-section">
        <div class="image-card" @mouseenter="hoverImage = true" @mouseleave="hoverImage = false">
          <ImageWithFallback :src="word.image_url" :word="word.word" />
          <div v-if="word.image_url && hoverImage" class="image-overlay">
            <button class="img-delete-btn" @click="handleClearImage" :disabled="deletingImage">
              <Trash2 :size="20" stroke-width="1.5" />
            </button>
          </div>
        </div>
        <div class="image-actions">
          <button
            class="btn btn-outline"
            @click="loadImage"
            :disabled="loadingImage"
          >
            {{ loadingImage ? '获取中...' : '获取图片' }}
          </button>
          <button
            v-if="word.image_url"
            class="btn btn-outline btn-img-del"
            @click="handleClearImage"
            :disabled="deletingImage"
          >
            {{ deletingImage ? '删除中...' : '删除图片' }}
          </button>
        </div>
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

          <div v-if="hasDictionaryData" class="dict-meanings">
            <div v-for="(m, i) in word.meanings" :key="i" class="meaning-item">
              <div class="meaning-header">
                <span class="pos-badge">{{ shortPos(m.pos) }}</span>
                <span class="meaning-def">{{ m.definition }}</span>
              </div>
              <div v-if="m.example" class="meaning-example">
                <p class="example-en">{{ m.example }}</p>
                <p v-if="m.example_cn" class="example-cn">{{ m.example_cn }}</p>
              </div>
            </div>
          </div>

          <p v-else-if="word.definition" class="text-secondary">{{ word.definition }}</p>
          <p v-else class="text-secondary">尚未加载</p>

          <button
            v-if="!hasDictionaryData"
            class="btn btn-outline mt-2"
            @click="loadDictionary"
            :disabled="loadingDict"
          >
            {{ loadingDict ? '加载中...' : '加载词典数据' }}
          </button>
        </div>

        <div v-if="word.example && !hasDictionaryData" class="section-card">
          <h3>例句</h3>
          <p class="example-text">{{ word.example }}</p>
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
  animation: detailFadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) both;
}

.image-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

@keyframes detailFadeIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

.image-actions {
  display: flex;
  gap: 8px;
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
  animation: detailFadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) both;
}

.section-card:nth-child(1) { animation-delay: 0s; }
.section-card:nth-child(2) { animation-delay: 0.06s; }
.section-card:nth-child(3) { animation-delay: 0.12s; }

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

.dict-meanings {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.meaning-item {
  padding: 10px 0;
}
.meaning-item + .meaning-item {
  border-top: 1px solid var(--border);
}

.meaning-header {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.pos-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  color: var(--primary);
  background: var(--bg);
  border: 1px solid var(--primary);
  padding: 1px 7px;
  border-radius: 4px;
  white-space: nowrap;
  flex-shrink: 0;
  line-height: 1.4;
}

.meaning-def {
  font-size: 14px;
  color: var(--text);
  line-height: 1.5;
}

.meaning-example {
  margin-top: 6px;
  margin-left: 4px;
  padding: 6px 10px;
  background: var(--bg);
  border-radius: 6px;
  border-left: 3px solid var(--border);
}

.example-en {
  font-size: 13px;
  font-style: italic;
  color: var(--text-secondary);
  margin: 0;
}

.example-cn {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 3px 0 0 0;
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
