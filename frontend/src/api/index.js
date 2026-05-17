import axios from 'axios'

const API_BASE = '/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
})

// Words
export function listWords(params = {}) {
  return api.get('/words', { params })
}

export function getWord(id) {
  return api.get(`/words/${id}`)
}

export function deleteWord(id) {
  return api.delete(`/words/${id}`)
}

export function importWords(file) {
  const form = new FormData()
  form.append('file', file)
  return api.post('/words/import', form)
}

export function fetchWordDict(id) {
  return api.post(`/words/${id}/dict`)
}

export function batchFillDict() {
  return api.post('/words/fill-dict')
}

export function batchTranslate() {
  return api.post('/words/batch-translate')
}

export function clearAllWords() {
  return api.delete('/words/clear-all')
}

// Media
export function getAudioUrl(id) {
  return `${API_BASE}/media/audio/${id}`
}

export function generateAudio(id) {
  return api.post(`/media/audio/${id}`)
}

export function fetchImage(id) {
  return api.post(`/media/image/${id}`)
}

export function clearImage(id) {
  return api.post(`/words/${id}/clear-image`)
}

// Review
export function getNextReview(stageFilter = 'due') {
  return api.post('/review/next', null, { params: { stage_filter: stageFilter } })
}

export function submitReview(data) {
  return api.post('/review/submit', data)
}

// Stats
export function getStats() {
  return api.get('/stats')
}

// Errors
export function getErrorWords() {
  return api.get('/review/errors')
}

export function clearErrorWord(wordId) {
  return api.post(`/review/errors/${wordId}/clear`)
}

export default api
