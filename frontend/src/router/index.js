import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
  },
  {
    path: '/words',
    name: 'WordList',
    component: () => import('../views/WordList.vue'),
  },
  {
    path: '/words/:id',
    name: 'WordDetail',
    component: () => import('../views/WordDetail.vue'),
  },
  {
    path: '/review/flash',
    name: 'ReviewFlash',
    component: () => import('../views/ReviewFlash.vue'),
  },
  {
    path: '/review/quiz',
    name: 'ReviewQuiz',
    component: () => import('../views/ReviewQuiz.vue'),
  },
  {
    path: '/review/errors',
    name: 'ReviewErrors',
    component: () => import('../views/ReviewErrors.vue'),
  },
  {
    path: '/import',
    name: 'Import',
    component: () => import('../views/Import.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
