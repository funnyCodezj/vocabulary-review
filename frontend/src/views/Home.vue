<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getStats } from '../api'

const router = useRouter()
const stats = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await getStats()
    stats.value = res.data
  } catch (e) {
    // server might not be running
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="home">
    <section class="hero-section">
      <h1 class="hero-title">单词复习</h1>
      <p class="hero-subtitle">通过间隔重复，高效掌握你的单词</p>
    </section>

    <section class="quick-actions">
      <div class="action-card" @click="router.push('/review/flash')">
        <span class="action-icon">🔄</span>
        <div>
          <h3>翻卡复习</h3>
          <p>翻转卡片回忆释义</p>
        </div>
      </div>
      <div class="action-card" @click="router.push('/review/quiz')">
        <span class="action-icon">✍️</span>
        <div>
          <h3>测验</h3>
          <p>四选一选中文</p>
        </div>
      </div>
      <div class="action-card" @click="router.push('/words')">
        <span class="action-icon">📚</span>
        <div>
          <h3>单词列表</h3>
          <p>浏览所有单词</p>
        </div>
      </div>
      <div class="action-card" @click="router.push('/review/errors')">
        <span class="action-icon">❌</span>
        <div>
          <h3>错题集</h3>
          <p>回顾答错的单词</p>
        </div>
      </div>
    </section>

    <section v-if="loading" class="loading-section">
      <p class="text-secondary">加载中...</p>
    </section>

    <section v-else-if="stats" class="stats-section">
      <h2 class="section-title">学习进度</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-value">{{ stats.total_words }}</span>
          <span class="stat-label">全部单词</span>
        </div>
        <div class="stat-card accent-new">
          <span class="stat-value">{{ stats.stage_0_new }}</span>
          <span class="stat-label">新词</span>
        </div>
        <div class="stat-card accent-learn">
          <span class="stat-value">{{ stats.stage_1_learning }}</span>
          <span class="stat-label">学习中</span>
        </div>
        <div class="stat-card accent-known">
          <span class="stat-value">{{ stats.stage_4_5_known }}</span>
          <span class="stat-label">已掌握</span>
        </div>
      </div>
      <div class="today-section">
        <h3 class="section-subtitle">今日学习</h3>
        <div class="today-grid">
          <div class="today-stat">
            <span class="today-value">{{ stats.today_reviewed }}</span>
            <span class="today-label">已复习</span>
          </div>
          <div class="today-stat">
            <span class="today-value">{{ stats.today_correct }}</span>
            <span class="today-label">正确</span>
          </div>
          <div class="today-stat">
            <span class="today-value" :class="{ 'text-success': stats.today_accuracy >= 80, 'text-warning': stats.today_accuracy < 80 && stats.today_accuracy > 0 }">
              {{ stats.today_accuracy }}%
            </span>
            <span class="today-label">正确率</span>
          </div>
        </div>
      </div>
    </section>

    <section v-else class="empty-section">
      <div class="empty-state">
        <p class="empty-icon">📖</p>
        <h3>开始学习</h3>
        <p class="text-secondary">导入你的单词列表开始复习</p>
        <button class="btn btn-primary mt-4" @click="router.push('/import')">
          导入单词
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home {
  max-width: 800px;
  margin: 0 auto;
}

.hero-section {
  text-align: center;
  padding: 40px 0 32px;
}

.hero-title {
  font-size: 36px;
  font-weight: 800;
  color: var(--text);
  margin: 0;
}

.hero-subtitle {
  color: var(--text-secondary);
  margin-top: 8px;
  font-size: 16px;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 32px;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s;
}

.action-card:hover {
  border-color: var(--primary-light);
  box-shadow: var(--shadow);
  transform: translateY(-2px);
}

.action-card h3 {
  font-size: 15px;
  font-weight: 600;
  margin: 0;
  color: var(--text);
}

.action-card p {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 2px 0 0;
}

.action-icon {
  font-size: 28px;
}

.stats-section {
  margin-bottom: 40px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px 16px;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 32px;
  font-weight: 800;
  color: var(--text);
}

.stat-label {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.accent-new .stat-value { color: #64748b; }
.accent-learn .stat-value { color: #d97706; }
.accent-known .stat-value { color: #059669; }

.today-section {
  margin-top: 20px;
}

.section-subtitle {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
}

.today-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.today-stat {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  text-align: center;
}

.today-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
}

.today-label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.text-success { color: var(--success); }
.text-warning { color: var(--warning); }
.text-secondary { color: var(--text-secondary); }

.empty-section {
  text-align: center;
  padding: 60px 0;
}

.empty-state h3 {
  font-size: 20px;
  margin: 12px 0 4px;
}

.empty-icon {
  font-size: 48px;
}

@media (max-width: 640px) {
  .quick-actions { grid-template-columns: 1fr; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .today-grid { grid-template-columns: repeat(3, 1fr); }
}
</style>
