<script setup>
import NavBar from './components/NavBar.vue'
import ToastContainer from './components/ToastContainer.vue'
</script>

<template>
  <NavBar />
  <main>
    <router-view v-slot="{ Component }">
      <transition name="page" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </main>
  <ToastContainer />
</template>

<style scoped>
main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 20px;
}

.page-enter-active {
  animation: pageIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.page-leave-active {
  animation: pageOut 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes pageIn {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pageOut {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-8px);
  }
}
</style>
