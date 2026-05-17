<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { RotateCw, ClipboardList, BookOpen, AlertTriangle, BookHeart } from 'lucide-vue-next'
import { getStats } from '../api'

const router = useRouter()
const stats = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await getStats()
    stats.value = res.data
  } catch {
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
        <RotateCw class="action-icon" :size="28" stroke-width="1.5" />
        <div>
          <h3>翻卡复习</h3>
          <p>翻转卡片回忆释义</p>
        </div>
      </div>
      <div class="action-card" @click="router.push('/review/quiz')">
        <ClipboardList class="action-icon" :size="28" stroke-width="1.5" />
        <div>
          <h3>测验</h3>
          <p>四选一选中文</p>
        </div>
      </div>
      <div class="action-card" @click="router.push('/words')">
        <BookOpen class="action-icon" :size="28" stroke-width="1.5" />
        <div>
          <h3>单词列表</h3>
          <p>浏览所有单词</p>
        </div>
      </div>
      <div class="action-card" @click="router.push('/review/errors')">
        <AlertTriangle class="action-icon" :size="28" stroke-width="1.5" />
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
        <div class="stat-card stagger-in" style="--i:0" @click="router.push('/words')">
          <span class="stat-value">{{ stats.total_words }}</span>
          <span class="stat-label">全部单词</span>
        </div>
        <div class="stat-card accent-new stagger-in tooltip-trigger" style="--i:1" @click="router.push('/words?filter=new')">
          <span class="stat-value">{{ stats.stage_0_new }}</span>
          <span class="stat-label">新词</span>
          <div class="tooltip-box">
            <p>从未复习过的单词，或者曾经答错被重置回起点的单词。</p>
          </div>
        </div>
        <div class="stat-card accent-learn stagger-in" style="--i:2" @click="router.push('/words?filter=learning')">
          <span class="stat-value">{{ stats.stage_1_learning }}</span>
          <span class="stat-label">学习中</span>
        </div>
        <div class="stat-card accent-known stagger-in tooltip-trigger" style="--i:3" @click="router.push('/words?filter=mastered')">
          <span class="stat-value">{{ stats.stage_4_5_known }}</span>
          <span class="stat-label">已掌握</span>
          <div class="tooltip-box">
            <p>连续答对 4 次以上，复习间隔逐渐拉长到超过 21 天，系统认为你已记住这个单词，不再频繁提醒复习。</p>
          </div>
        </div>
      </div>
      <div class="today-section">
        <h3 class="section-subtitle">今日学习</h3>
        <div class="today-grid">
          <div class="today-stat stagger-in tooltip-trigger" style="--i:4">
            <span class="today-value">{{ stats.today_reviewed }}</span>
            <span class="today-label">已复习/测试</span>
            <div class="tooltip-box">
              <p>今日在翻卡复习和测验中完成的题目总数，两个模式共用同一份数据。</p>
            </div>
          </div>
          <div class="today-stat stagger-in tooltip-trigger" style="--i:5">
            <span class="today-value">{{ stats.today_correct }}</span>
            <span class="today-label">正确</span>
            <div class="tooltip-box">
              <p>今日翻卡复习中自评「有点难」及以上、测验中选对答案，都算正确。</p>
            </div>
          </div>
          <div class="today-stat stagger-in tooltip-trigger" style="--i:6">
            <span class="today-value" :class="{ 'text-success': stats.today_accuracy >= 80, 'text-warning': stats.today_accuracy < 80 && stats.today_accuracy > 0 }">
              {{ stats.today_accuracy }}%
            </span>
            <span class="today-label">正确率</span>
            <div class="tooltip-box">
              <p>正确数 ÷ 已复习/测试总数，翻卡复习和测验合并计算。</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section v-else class="empty-section">
      <div class="empty-state">
        <BookHeart class="empty-icon" :size="48" stroke-width="1" />
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
  letter-spacing: -0.02em;
  animation: heroTextIn 0.5s cubic-bezier(0.4, 0, 0.2, 1) both;
}

.hero-subtitle {
  color: var(--text-secondary);
  margin-top: 8px;
  font-size: 16px;
  animation: heroTextIn 0.5s cubic-bezier(0.4, 0, 0.2, 1) both;
  animation-delay: 0.1s;
}

@keyframes heroTextIn {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
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
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: actionCardIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) both;
}

.action-card:nth-child(1) { animation-delay: 0s; }
.action-card:nth-child(2) { animation-delay: 0.06s; }
.action-card:nth-child(3) { animation-delay: 0.12s; }
.action-card:nth-child(4) { animation-delay: 0.18s; }

@keyframes actionCardIn {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

.action-card:hover {
  border-color: var(--primary-light);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.12);
  transform: translateY(-3px);
}

.action-card:active {
  transform: translateY(-1px) scale(0.99);
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
  flex-shrink: 0;
  color: var(--primary);
}

.stats-section {
  margin-bottom: 40px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 16px;
  animation: fadeSlideIn 0.4s ease both;
}

.section-subtitle {
  animation: fadeSlideIn 0.4s ease both;
  animation-delay: 0.15s;
}

.stagger-in {
  animation: cardPopIn 0.45s cubic-bezier(0.4, 0, 0.2, 1) both;
  animation-delay: calc(var(--i) * 0.06s);
}

@keyframes cardPopIn {
  from {
    opacity: 0;
    transform: translateY(16px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
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
  cursor: pointer;
  transition: all 0.2s;
}

.stat-card:hover {
  border-color: var(--primary-light);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.1);
  transform: translateY(-2px);
}

.stat-value {
  display: block;
  font-size: 32px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.02em;
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

.tooltip-trigger {
  position: relative;
}

.stat-card.tooltip-trigger {
  cursor: pointer;
}

.tooltip-box {
  display: none;
  position: absolute;
  bottom: calc(100% + 10px);
  left: 50%;
  transform: translateX(-50%);
  width: 260px;
  padding: 14px 16px;
  background: #1e293b;
  color: #e2e8f0;
  font-size: 13px;
  line-height: 1.6;
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 24px rgba(0,0,0,0.25);
  z-index: 10;
  text-align: left;
}

.tooltip-box::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 8px solid transparent;
  border-top-color: #1e293b;
}

.tooltip-trigger:hover .tooltip-box {
  display: block;
}

.tooltip-trigger:hover .tooltip-box p {
  margin: 0;
}

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
  transition: box-shadow 0.2s ease;
}

.today-stat:hover {
  box-shadow: var(--shadow-md);
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
  color: var(--text-secondary);
  opacity: 0.4;
  margin-bottom: 8px;
}

@media (max-width: 640px) {
  .quick-actions { grid-template-columns: 1fr; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .today-grid { grid-template-columns: repeat(3, 1fr); }
}
</style>
