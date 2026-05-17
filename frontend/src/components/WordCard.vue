<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { deleteWord } from '../api'
import ImageWithFallback from './ImageWithFallback.vue'
import AudioButton from './AudioButton.vue'

const props = defineProps({
  word: { type: Object, required: true },
})

const emit = defineEmits(['deleted'])

const router = useRouter()
const deleting = ref(false)

function stageLabel(stage) {
  const labels = ['新词', '学习中', '复习', '复习', '已掌握', '已精通']
  return labels[stage] || '新词'
}

async function handleDelete(e) {
  e.stopPropagation()
  if (!confirm(`确定删除单词「${props.word.word}」？`)) return
  deleting.value = true
  try {
    await deleteWord(props.word.id)
    emit('deleted', props.word.id)
  } catch {
    alert('删除失败')
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div class="word-card" @click="router.push(`/words/${word.id}`)">
    <div class="card-image">
      <ImageWithFallback :src="word.image_url" :word="word.word" />
      <button class="delete-btn" @click="handleDelete" :disabled="deleting" title="删除">
        ✕
      </button>
    </div>
    <div class="card-body">
      <div class="card-header">
        <h3 class="word-text">{{ word.word }}</h3>
        <span class="stage-badge" :class="`stage-${word.stage || 0}`">
          {{ stageLabel(word.stage) }}
        </span>
      </div>
      <p class="phonetic">{{ word.phonetic || word.word }}</p>
      <p class="definition">{{ word.definition ? word.definition.slice(0, 60) + (word.definition.length > 60 ? '...' : '') : '' }}</p>
      <p v-if="word.chinese" class="chinese">{{ word.chinese }}</p>
      <div class="card-footer">
        <AudioButton :word="word.word" />
        <span v-if="word.next_review_date" class="next-review">
          下次复习: {{ word.next_review_date }}
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.word-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow);
  position: relative;
  animation: cardEnter 0.4s cubic-bezier(0.4, 0, 0.2, 1) both;
}

@keyframes cardEnter {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.word-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 20px -8px rgba(0,0,0,0.12), 0 4px 8px -2px rgba(0,0,0,0.06);
  border-color: var(--primary-light);
}

.card-image {
  width: 100%;
  height: 160px;
  overflow: hidden;
  background: #f1f5f9;
  position: relative;
}

.delete-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 50%;
  background: rgba(0,0,0,0.45);
  color: white;
  font-size: 14px;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-image:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: var(--error);
}

.card-body {
  padding: 14px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.word-text {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
  margin: 0;
}

.stage-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 20px;
  letter-spacing: 0.5px;
}

.stage-0 { background: #e2e8f0; color: #64748b; }
.stage-1 { background: #fef3c7; color: #92400e; }
.stage-2 { background: #dbeafe; color: #1e40af; }
.stage-3 { background: #d1fae5; color: #065f46; }
.stage-4 { background: #d1fae5; color: #065f46; }
.stage-5 { background: #fae8ff; color: #6b21a8; }

.phonetic {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.definition {
  font-size: 13px;
  color: var(--text);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.chinese {
  font-size: 13px;
  color: var(--primary);
  margin-top: 2px;
  font-weight: 500;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--border);
}

.next-review {
  font-size: 11px;
  color: var(--text-secondary);
}
</style>
