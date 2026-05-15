<script setup>
import { ref, onMounted, watch } from 'vue'
import { listWords, clearAllWords } from '../api'
import WordCard from '../components/WordCard.vue'

const words = ref([])
const total = ref(0)
const page = ref(1)
const search = ref('')
const loading = ref(false)
const clearing = ref(false)
const sortBy = ref('word')
const sortOrder = ref('asc')

const showClearConfirm = ref(false)
const clearConfirmText = ref('')

const pageSize = 50

async function fetchWords() {
  loading.value = true
  try {
    const res = await listWords({
      page: page.value,
      page_size: pageSize,
      search: search.value || undefined,
      sort_by: sortBy.value,
      sort_order: sortOrder.value,
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

onMounted(fetchWords)

let searchTimer
watch(search, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    fetchWords()
  }, 300)
})

const totalPages = () => Math.ceil(total.value / pageSize)

function setSort(by) {
  if (sortBy.value === by) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = by
    sortOrder.value = by === 'word' ? 'asc' : 'desc'
  }
  page.value = 1
  fetchWords()
}
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

    <div class="sort-bar">
      <span class="sort-label">排序：</span>
      <button
        class="sort-btn"
        :class="{ active: sortBy === 'word' }"
        @click="setSort('word')"
      >
        字母 {{ sortBy === 'word' ? (sortOrder === 'asc' ? '↑' : '↓') : '' }}
      </button>
      <button
        class="sort-btn"
        :class="{ active: sortBy === 'stage' }"
        @click="setSort('stage')"
      >
        熟练度 {{ sortBy === 'stage' ? (sortOrder === 'asc' ? '↑' : '↓') : '' }}
      </button>
    </div>

    <div v-if="loading" class="loading">
      <p class="text-secondary">加载中...</p>
    </div>

    <div v-else-if="words.length === 0" class="empty">
      <p class="text-secondary">还没有单词，去导入吧。</p>
    </div>

    <div v-else class="word-grid">
      <WordCard
        v-for="w in words"
        :key="w.id"
        :word="w"
        @deleted="onWordDeleted"
      />
    </div>

    <div v-if="totalPages() > 1" class="pagination">
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

.sort-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.sort-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.sort-btn {
  padding: 5px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg-card);
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.sort-btn:hover {
  border-color: var(--primary-light);
  color: var(--text);
}

.sort-btn.active {
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

.loading, .empty {
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
