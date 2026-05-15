<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { importWords, batchFillDict, batchTranslate } from '../api'

const router = useRouter()
const importing = ref(false)
const result = ref(null)
const error = ref('')

async function handleFileUpload(e) {
  const file = e.target.files[0]
  if (!file) return

  importing.value = true
  error.value = ''
  result.value = null

  try {
    const res = await importWords(file)
    result.value = res.data
  } catch (err) {
    error.value = '导入失败，请确认后端服务是否运行'
    console.error(err)
  } finally {
    importing.value = false
  }
}

async function fillDictionary() {
  try {
    const res = await batchFillDict()
    alert(`已填充 ${res.data.filled} 个单词，剩余 ${res.data.remaining} 个`)
  } catch (err) {
    alert('获取词典数据失败')
  }
}

async function handleBatchTranslate() {
  try {
    const res = await batchTranslate()
    alert(`已翻译 ${res.data.translated} 个单词，剩余 ${res.data.remaining} 个`)
  } catch (err) {
    alert('翻译失败')
  }
}
</script>

<template>
  <div class="import-page">
    <h1 class="page-title">导入单词</h1>
    <p class="page-desc">上传 TXT 或 JSON 文件</p>

    <div class="card upload-card">
      <div class="upload-zone">
        <label class="upload-btn" :class="{ disabled: importing }">
          <input
            type="file"
            accept=".txt,.json"
            @change="handleFileUpload"
            :disabled="importing"
            hidden
          />
          <span v-if="importing" class="upload-text">导入中...</span>
          <span v-else class="upload-text">
            <span class="upload-icon">📁</span>
            选择 TXT / JSON 文件
          </span>
        </label>
        <p class="text-sm text-secondary mt-2">TXT: 每行一个单词，可选格式: 单词,音标。JSON: 数组格式 {"en": "单词", "zh": "中文"}</p>
      </div>

      <div v-if="result" class="result-box">
        <p class="result-icon">✅</p>
        <p>成功导入 <strong>{{ result.imported }}</strong> 个单词</p>
        <p v-if="result.updated > 0" class="text-sm text-success">{{ result.updated }} 个已有单词更新了中文翻译</p>
        <p v-if="result.skipped > 0" class="text-sm text-secondary">{{ result.skipped }} 个重复已跳过</p>
        <div class="result-actions">
          <button class="btn btn-outline" @click="fillDictionary">批量获取词典数据</button>
          <button class="btn btn-outline" @click="handleBatchTranslate">批量获取中文翻译</button>
          <button class="btn btn-primary" @click="router.push('/words')">查看单词</button>
        </div>
      </div>

      <p v-if="error" class="error-msg">{{ error }}</p>
    </div>

    <div class="card tips-card">
      <h3>格式说明</h3>
      <p class="text-sm font-bold">TXT 格式（每行一个单词）</p>
      <pre class="example">
apple
banana,ˈbæn.ə.nə
cherry</pre>
      <p class="text-sm font-bold mt-2">JSON 格式（含中文翻译）</p>
      <pre class="example">[
  {"en": "apple", "zh": "苹果"},
  {"en": "banana", "zh": "香蕉"}
]</pre>
      <p class="text-sm text-secondary mt-2">
        导入后点击"批量获取词典数据"自动从 Free Dictionary API 获取音标和释义。
      </p>
    </div>
  </div>
</template>

<style scoped>
.import-page {
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

.upload-card {
  padding: 32px;
  text-align: center;
}

.upload-zone {
  margin-bottom: 16px;
}

.upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  border: 2px dashed var(--border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s;
  background: transparent;
}

.upload-btn:hover {
  border-color: var(--primary);
  background: rgba(79, 70, 229, 0.04);
}

.upload-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.upload-icon {
  font-size: 20px;
}

.upload-text {
  font-weight: 600;
  color: var(--text);
}

.result-box {
  margin-top: 20px;
  padding: 16px;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: var(--radius);
}

.result-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin-top: 12px;
}

.error-msg {
  color: var(--error);
  font-size: 14px;
  margin-top: 12px;
}

.tips-card {
  padding: 24px;
  margin-top: 16px;
}

.tips-card h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.example {
  background: var(--bg);
  padding: 12px;
  border-radius: var(--radius);
  font-family: ui-monospace, monospace;
  font-size: 13px;
  line-height: 1.6;
}
</style>
