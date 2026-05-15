<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const nav = [
  { name: '首页', path: '/', icon: '📊' },
  { name: '单词', path: '/words', icon: '📚' },
  { name: '复习', path: '/review/flash', icon: '🔄' },
  { name: '测验', path: '/review/quiz', icon: '✍️' },
  { name: '错题', path: '/review/errors', icon: '❌' },
  { name: '导入', path: '/import', icon: '📥' },
]
</script>

<template>
  <header class="navbar">
    <div class="navbar-inner">
      <div class="logo" @click="router.push('/')">
        <span class="logo-icon">V</span>
        <span class="logo-text">VocabReview</span>
      </div>
      <nav class="nav-links">
        <router-link
          v-for="item in nav"
          :key="item.path"
          :to="item.path"
          class="nav-link"
          active-class="active"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.name }}</span>
        </router-link>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.navbar {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
}

.logo-icon {
  width: 34px;
  height: 34px;
  background: var(--primary);
  color: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 16px;
}

.logo-text {
  font-weight: 700;
  font-size: 18px;
  color: var(--text);
}

.nav-links {
  display: flex;
  gap: 4px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: var(--radius);
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.nav-link:hover {
  color: var(--text);
  background: var(--bg);
  text-decoration: none;
}

.nav-link.active {
  color: var(--primary);
  background: rgba(79, 70, 229, 0.08);
}

.nav-icon {
  font-size: 16px;
}

@media (max-width: 640px) {
  .nav-label {
    display: none;
  }
  .nav-link {
    padding: 8px 10px;
  }
}
</style>
