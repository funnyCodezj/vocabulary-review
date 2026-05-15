<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getErrorWords } from '../api'

const router = useRouter()
const words = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await getErrorWords()
    words.value = res.data.items
  } catch {
    // server error
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="errors-page">
    <h1 class="page-title">错题集</h1>
    <p class="page-desc">历史上回答错误的单词</p>

    <div v-if="loading" class="loading-section">
      <p class="text-secondary">加载中...</p>
    </div>

    <div v-else-if="words.length === 0" class="empty-section">
      <p class="empty-icon">🎉</p>
      <h3>暂无错题</h3>
      <p class="text-secondary">继续保持！</p>
    </div>

    <div v-else class="error-list">
      <div
        v-for="w in words"
        :key="w.id"
        class="error-card card"
        @click="router.push(`/words/${w.id}?from=errors`)"
      >
        <div class="error-left">
          <h3 class="error-word">{{ w.word }}</h3>
          <p v-if="w.chinese" class="error-chinese">{{ w.chinese }}</p>
          <p v-else-if="w.definition" class="error-def">{{ w.definition }}</p>
        </div>
        <div class="error-right">
          <span class="error-count">{{ w.incorrect_count }}</span>
          <span class="error-label">次错误</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.errors-page {
  max-width: 600px;
  margin: 0 auto;
}

.page-title {
  font-size: 28px;
  font-weight: 800;
  margin-bottom: 4px;
}

.page-desc {
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.loading-section, .empty-section {
  text-align: center;
  padding: 60px 0;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.error-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.error-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.error-card:hover {
  border-color: var(--error);
  box-shadow: var(--shadow);
}

.error-left {
  flex: 1;
}

.error-word {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 2px;
}

.error-chinese {
  font-size: 14px;
  color: var(--primary);
  font-weight: 500;
}

.error-def {
  font-size: 13px;
  color: var(--text-secondary);
}

.error-right {
  text-align: center;
  flex-shrink: 0;
  margin-left: 16px;
}

.error-count {
  display: block;
  font-size: 24px;
  font-weight: 800;
  color: var(--error);
  line-height: 1;
}

.error-label {
  font-size: 11px;
  color: var(--text-secondary);
}
</style>
