<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { FolderUp, Package, Download, CheckCircle, AlertTriangle, XCircle } from 'lucide-vue-next'
import { importWords, batchFillDict, batchTranslate, exportBackup, importBackup } from '../api'
import { useToast } from '../composables/useToast'

const router = useRouter()
const { show: showToast } = useToast()

const activeTab = ref('import')

// --- Import new words ---
const importing = ref(false)
const result = ref(null)
const error = ref('')
const dictLoading = ref(false)
const translateLoading = ref(false)

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
  dictLoading.value = true
  showToast('正在获取词典数据，可以离开当前页面，处理会在后台进行...', 'info')
  try {
    const res = await batchFillDict()
    showToast(`已填充 ${res.data.filled} 个单词，剩余 ${res.data.remaining} 个`, 'success')
  } catch {
    showToast('获取词典数据失败', 'error')
  } finally {
    dictLoading.value = false
  }
}

async function handleBatchTranslate() {
  translateLoading.value = true
  showToast('正在获取中文翻译，可以离开当前页面，处理会在后台进行...', 'info')
  try {
    const res = await batchTranslate()
    showToast(`已翻译 ${res.data.translated} 个单词，剩余 ${res.data.remaining} 个`, 'success')
  } catch {
    showToast('获取中文翻译失败', 'error')
  } finally {
    translateLoading.value = false
  }
}

// --- Export ---
const exporting = ref(false)

async function handleExport() {
  exporting.value = true
  try {
    const res = await exportBackup()
    const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `vocab-review-backup-${new Date().toISOString().slice(0, 10)}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    showToast(`导出成功：${res.data.words.length} 个单词`, 'success')
  } catch {
    showToast('导出失败', 'error')
  } finally {
    exporting.value = false
  }
}

// --- Import user data ---
const restoring = ref(false)
const showRestoreConfirm = ref(false)
const restoreFile = ref(null)
const restoreConfirmText = ref('')
const restoreResult = ref(null)

function onRestoreFileSelected(e) {
  const file = e.target.files[0]
  if (!file) return
  restoreFile.value = file
  restoreConfirmText.value = ''
  restoreResult.value = null
  showRestoreConfirm.value = true
}

async function handleRestore() {
  if (!restoreFile.value) return
  restoring.value = true
  try {
    const text = await restoreFile.value.text()
    const data = JSON.parse(text)
    const res = await importBackup(data)
    restoreResult.value = res.data
    showRestoreConfirm.value = false
    restoreConfirmText.value = ''
    restoreFile.value = null
    showToast(`数据恢复完成：${res.data.words} 个单词，${res.data.progress} 条进度`, 'success')
  } catch {
    showToast('数据恢复失败，请确认文件格式正确', 'error')
  } finally {
    restoring.value = false
  }
}
</script>

<template>
  <div class="import-page">
    <h1 class="page-title">导入 / 导出</h1>

    <!-- Tabs -->
    <div class="tab-bar">
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'import' }"
        @click="activeTab = 'import'"
      >导入新单词</button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'export' }"
        @click="activeTab = 'export'"
      >导出用户数据</button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'restore' }"
        @click="activeTab = 'restore'"
      >导入用户数据</button>
    </div>

    <!-- Tab: Import new words -->
    <div v-if="activeTab === 'import'" class="tab-content">
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
              <FolderUp class="upload-icon" :size="20" stroke-width="1.5" />
              选择 TXT / JSON 文件
            </span>
          </label>
          <p class="text-sm text-secondary mt-2">TXT: 每行一个单词，可选格式: 单词 中文。JSON: 数组格式 {"en": "单词", "zh": "中文"}</p>
        </div>

        <div v-if="result" class="result-box">
          <CheckCircle class="result-icon" :size="24" stroke-width="1.5" />
          <p>成功导入 <strong>{{ result.imported }}</strong> 个单词</p>
          <p v-if="result.updated > 0" class="text-sm text-success">{{ result.updated }} 个已有单词更新了中文翻译</p>
          <p v-if="result.skipped > 0" class="text-sm text-secondary">{{ result.skipped }} 个重复已跳过</p>
          <div class="result-actions">
            <button class="btn btn-outline" :disabled="dictLoading" @click="fillDictionary">
              {{ dictLoading ? '获取中...' : '批量获取词典数据' }}
            </button>
            <button class="btn btn-outline" :disabled="translateLoading" @click="handleBatchTranslate">
              {{ translateLoading ? '获取中...' : '批量获取中文翻译' }}
            </button>
            <button class="btn btn-primary" @click="router.push('/words')">查看单词</button>
          </div>
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>
      </div>

      <div class="card tips-card">
        <h3>格式说明</h3>
        <p class="text-sm font-bold">TXT 格式（每行一个单词，单词 中文）</p>
        <pre class="example">
apple 苹果
banana 香蕉
cherry</pre>
        <p class="text-sm font-bold mt-2">JSON 格式（含中文翻译）</p>
        <pre class="example">[
  {"en": "apple", "zh": "苹果"},
  {"en": "banana", "zh": "香蕉"}
]</pre>
        <p class="text-sm text-secondary mt-2">导入后点击"批量获取词典数据"自动获取音标和释义。</p>
      </div>
    </div>

    <!-- Tab: Export -->
    <div v-if="activeTab === 'export'" class="tab-content">
      <div class="card export-card">
        <Package class="export-icon" :size="48" stroke-width="1" />
        <h3>导出全部数据</h3>
        <p class="text-secondary">导出所有单词、复习记录、错题等数据为 JSON 文件，可用于备份或迁移到其他设备。</p>
        <button class="btn btn-primary mt-4" :disabled="exporting" @click="handleExport">
          {{ exporting ? '导出中...' : '导出数据' }}
        </button>
      </div>
    </div>

    <!-- Tab: Restore -->
    <div v-if="activeTab === 'restore'" class="tab-content">
      <div class="card restore-card">
        <Download class="restore-icon" :size="48" stroke-width="1" />
        <h3>导入用户数据</h3>
        <p class="text-secondary">选择之前导出的备份 JSON 文件，恢复全部单词、复习记录和错题数据。</p>
        <label class="upload-btn mt-4" :class="{ disabled: restoring }">
          <input
            type="file"
            accept=".json"
            @change="onRestoreFileSelected"
            :disabled="restoring"
            hidden
          />
          <span class="upload-text">
            <FolderUp :size="20" stroke-width="1.5" />
            选择备份文件
          </span>
        </label>
        <p v-if="restoreResult" class="text-sm text-success mt-2">
          已恢复 {{ restoreResult.words }} 个单词，{{ restoreResult.progress }} 条学习进度
        </p>
      </div>
    </div>

    <!-- Restore confirmation modal -->
    <Teleport to="body">
      <div v-if="showRestoreConfirm" class="modal-overlay" @click.self="showRestoreConfirm = false">
        <div class="modal-card card">
          <AlertTriangle class="modal-warn-icon" :size="40" stroke-width="1.5" />
          <h3 class="modal-title">重要提醒</h3>
          <p class="text-secondary text-sm">
            此操作将<strong>彻底覆盖</strong>当前所有数据，包括单词、复习记录、错题等，<strong>不可恢复</strong>！
          </p>
          <p class="text-sm mt-2">
            请输入 <strong>确认覆盖</strong> 以继续：
          </p>
          <input
            v-model="restoreConfirmText"
            type="text"
            placeholder="确认覆盖"
            class="modal-input"
            @keyup.enter="handleRestore"
          />
          <div class="modal-actions">
            <button class="btn btn-outline" @click="showRestoreConfirm = false">取消</button>
            <button
              class="btn btn-danger"
              :disabled="restoreConfirmText !== '确认覆盖' || restoring"
              @click="handleRestore"
            >
              {{ restoring ? '恢复中...' : '确认恢复' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
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
  letter-spacing: -0.02em;
}

/* Tabs */
.tab-bar {
  display: flex;
  gap: 0;
  margin: 20px 0;
  border-bottom: 2px solid var(--border);
}

.tab-btn {
  flex: 1;
  padding: 12px 16px;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  background: transparent;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.tab-btn:hover {
  color: var(--text);
}

.tab-btn.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
}

.tab-content {
  animation: tabIn 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes tabIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.upload-card, .export-card, .restore-card {
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
  font-family: inherit;
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
  flex-shrink: 0;
  color: var(--text);
}

.upload-text {
  font-weight: 600;
  color: var(--text);
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.result-box {
  margin-top: 20px;
  padding: 16px;
  background: var(--success-bg);
  border: 1px solid var(--success-border);
  border-radius: var(--radius);
}

.result-icon {
  color: var(--success);
  margin-bottom: 8px;
}

.result-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin-top: 12px;
  flex-wrap: wrap;
}

.result-actions .btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
  font-family: 'Inter', ui-monospace, monospace;
  font-size: 13px;
  line-height: 1.6;
}

/* Export & Restore cards */
.export-icon, .restore-icon {
  color: var(--primary);
  margin-bottom: 12px;
}

.export-card h3, .restore-card h3 {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
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
  text-align: center;
}

.modal-warn-icon {
  color: var(--warning);
  margin-bottom: 8px;
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

.btn-danger {
  background: var(--error);
  color: white;
  border: none;
}
.btn-danger:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.btn-danger:not(:disabled):hover {
  background: #dc2626;
}
</style>
