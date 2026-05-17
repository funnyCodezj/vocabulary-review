import { reactive } from 'vue'

const toasts = reactive([])
let nextId = 0

export function useToast() {
  function show(message, type = 'info', duration = 5000) {
    const id = nextId++
    toasts.push({ id, message, type })
    if (duration > 0) {
      setTimeout(() => dismiss(id), duration)
    }
    return id
  }

  function dismiss(id) {
    const idx = toasts.findIndex(t => t.id === id)
    if (idx !== -1) toasts.splice(idx, 1)
  }

  return { toasts, show, dismiss }
}
