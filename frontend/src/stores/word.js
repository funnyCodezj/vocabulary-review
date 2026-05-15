import { defineStore } from 'pinia'
import { listWords, getStats } from '../api'

export const useWordStore = defineStore('word', {
  state: () => ({
    words: [],
    total: 0,
    page: 1,
    pageSize: 50,
    search: '',
    stats: null,
    loading: false,
  }),
  actions: {
    async fetchWords() {
      this.loading = true
      try {
        const res = await listWords({
          page: this.page,
          page_size: this.pageSize,
          search: this.search || undefined,
        })
        this.words = res.data.items
        this.total = res.data.total
      } catch (e) {
        console.error('Failed to fetch words:', e)
      } finally {
        this.loading = false
      }
    },
    async fetchStats() {
      try {
        const res = await getStats()
        this.stats = res.data
      } catch (e) {
        console.error('Failed to fetch stats:', e)
      }
    },
  },
})
