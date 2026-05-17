<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import { listWords, clearAllWords } from '../api'
import WordCard from '../components/WordCard.vue'

const route = useRoute()
const router = useRouter()
const words = ref([])
const total = ref(0)
const page = ref(1)
const search = ref('')
const loading = ref(false)
const clearing = ref(false)
const stageFilter = ref('all')

const showClearConfirm = ref(false)
const clearConfirmText = ref('')

const pageSize = 50

const filterOptions = [
  { value: 'all', label: '全部单词' },
  { value: 'new', label: '新词' },
  { value: 'due', label: '待复习' },
  { value: 'learning', label: '学习中' },
  { value: 'reviewing', label: '复习中' },
  { value: 'mastered', label: '已掌握' },
  { value: 'errors', label: '错题' },
]

const skeletonItems = Array.from({ length: 8 })

function setFilter(value) {
  stageFilter.value = value
  page.value = 1
  sessionStorage.setItem('wordListFilter', value)
  router.replace({ query: { filter: value === 'all' ? undefined : value } })
  fetchWords()
}

async function fetchWords() {
  loading.value = true
  try {
    const res = await listWords({
      page: page.value,
      page_size: pageSize,
      search: search.value || undefined,
      stage_filter: stageFilter.value,
    })
    words.value = res.data.items
    total.value = res.data.total
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function onWordDeleted(id) {
  words.value = words.value.filter(w => w.id !== id)
  total.value--
}

async function handleClearAll() {
  if (clearConfirmText.value !== '确认删除所有单词') return
  clearing.value = true
  try {
    await clearAllWords()
    showClearConfirm.value = false
    clearConfirmText.value = ''
    page.value = 1
    await fetchWords()
  } catch {
    alert('清空失败')
  } finally {
    clearing.value = false
  }
}

onMounted(() => {
  if (route.query.filter) {
    stageFilter.value = route.query.filter
  } else {
    const saved = sessionStorage.getItem('wordListFilter')
    if (saved) {
      stageFilter.value = saved
      router.replace({ query: { filter: saved === 'all' ? undefined : saved } })
    }
  }
  fetchWords()
})

onBeforeRouteLeave((to) => {
  if (!to.path.startsWith('/words/')) {
    sessionStorage.removeItem('wordListFilter')
  }
})

let searchTimer
watch(search, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    fetchWords()
  }, 300)
})

const totalPages = () => Math.ceil(total.value / pageSize)
</script>

<template>
  <div class="word-list-page">
    <div class="header">
      <div class="header-left">
        <h1 class="page-title">单词列表</h1>
        <span class="word-count">共 {{ total }} 个单词</span>
      </div>
      <button
        v-if="total > 0"
        class="btn btn-outline btn-danger"
        @click="showClearConfirm = true"
      >
        清空全部
      </button>
    </div>

    <div class="search-bar">
      <input
        v-model="search"
        type="text"
        placeholder="搜索单词..."
        class="search-input"
      />
    </div>

    <div class="filter-bar">
      <button
        v-for="opt in filterOptions"
        :key="opt.value"
        class="filter-chip"
        :class="{ active: stageFilter === opt.value }"
        @click="setFilter(opt.value)"
      >
        {{ opt.label }}
      </button>
    </div>

    <!-- Skeleton loading -->
    <div v-if="loading" class="word-grid">
      <div v-for="i in skeletonItems" :key="i" class="skeleton-card">
        <div class="skeleton-image"></div>
        <div class="skeleton-body">
          <div class="skeleton-line w-60"></div>
          <div class="skeleton-line w-40"></div>
          <div class="skeleton-line w-80"></div>
          <div class="skeleton-line w-50"></div>
        </div>
      </div>
    </div>

    <div v-else-if="words.length === 0" class="empty">
      <p class="text-secondary">还没有单词，去导入吧。</p>
    </div>

    <div v-else class="word-grid">
      <WordCard
        v-for="(w, idx) in words"
        :key="w.id"
        :word="w"
        :style="{ animationDelay: (idx * 0.05) + 's' }"
        @deleted="onWordDeleted"
      />
    </div>

    <div v-if="!loading && totalPages() > 1" class="pagination">
      <button
        class="btn btn-outline"
        :disabled="page <= 1"
        @click="page--; fetchWords()"
      >
        上一页
      </button>
      <span class="page-info">{{ page }} / {{ totalPages() }}</span>
      <button
        class="btn btn-outline"
        :disabled="page >= totalPages()"
        @click="page++; fetchWords()"
      >
        下一页
      </button>
    </div>

    <!-- 清空确认弹窗 -->
    <Teleport to="body">
      <div v-if="showClearConfirm" class="modal-overlay" @click.self="showClearConfirm = false">
        <div class="modal-card card">
          <h3 class="modal-title">确认清空所有单词</h3>
          <p class="text-secondary text-sm">
            此操作不可恢复！将删除全部 {{ total }} 个单词及其复习记录。
          </p>
          <p class="text-sm mt-2">
            请输入 <strong>确认删除所有单词</strong> 以确认：
          </p>
          <input
            v-model="clearConfirmText"
            type="text"
            placeholder="确认删除所有单词"
            class="modal-input"
            @keyup.enter="handleClearAll"
          />
          <div class="modal-actions">
            <button class="btn btn-outline" @click="showClearConfirm = false">
              取消
            </button>
            <button
              class="btn btn-danger"
              :disabled="clearConfirmText !== '确认删除所有单词' || clearing"
              @click="handleClearAll"
            >
              {{ clearing ? '删除中...' : '确认清空' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.page-title {
  font-size: 28px;
  font-weight: 800;
  margin: 0;
  letter-spacing: -0.02em;
}

.word-count {
  font-size: 14px;
  color: var(--text-secondary);
}

.btn-danger {
  color: var(--error);
  border-color: var(--error);
}

.btn-danger:hover {
  background: var(--error);
  color: white;
}

.search-bar {
  margin-bottom: 20px;
}

.search-input {
  width: 100%;
  max-width: 400px;
  padding: 10px 14px;
}

.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.filter-chip {
  padding: 6px 16px;
  border: 1px solid var(--border);
  border-radius: 20px;
  background: var(--bg-card);
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary);
  transition: all 0.2s;
  font-family: inherit;
}

.filter-chip:hover {
  border-color: var(--primary-light);
  color: var(--text);
}

.filter-chip.active {
  border-color: var(--primary);
  background: rgba(79, 70, 229, 0.06);
  color: var(--primary);
  font-weight: 600;
}

.word-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.empty {
  text-align: center;
  padding: 60px 0;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
  padding: 16px 0;
}

.page-info {
  font-size: 14px;
  color: var(--text-secondary);
  min-width: 60px;
  text-align: center;
}

/* Skeleton */
.skeleton-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--border);
}

.skeleton-image {
  height: 160px;
  background: linear-gradient(90deg, #e2e8f0 25%, #f1f5f9 50%, #e2e8f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}

.skeleton-body {
  padding: 16px;
}

.skeleton-line {
  height: 14px;
  background: linear-gradient(90deg, #e2e8f0 25%, #f1f5f9 50%, #e2e8f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
  border-radius: 4px;
  margin-bottom: 10px;
}

.skeleton-line:last-child {
  margin-bottom: 0;
}

.w-40 { width: 40%; }
.w-50 { width: 50%; }
.w-60 { width: 60%; }
.w-80 { width: 80%; }

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.modal-card {
  padding: 28px;
  max-width: 420px;
  width: 90%;
}

.modal-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
}

.modal-input {
  width: 100%;
  padding: 10px 12px;
  margin-top: 8px;
  box-sizing: border-box;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 16px;
}

.btn.btn-danger {
  background: var(--error);
  color: white;
  border: none;
}
.btn.btn-danger:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.btn.btn-danger:not(:disabled):hover {
  background: #dc2626;
}
</style>
