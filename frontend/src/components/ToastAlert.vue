<template>
  <!-- Teleports toast notifications to body top-right corner -->
  <Teleport to="body">
    <div class="pp-toast-container">
      <transition-group name="toast-fade">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="toast show align-items-center border-0"
          :class="toast.type === 'success' ? 'bg-success text-white' : toast.type === 'danger' ? 'bg-danger text-white' : 'bg-warning text-dark'"
          role="alert"
          style="min-width:280px; border-radius:10px; box-shadow:0 4px 20px rgba(0,0,0,0.15);"
        >
          <div class="d-flex">
            <div class="toast-body d-flex align-items-center gap-2">
              <i :class="toast.type === 'success' ? 'bi bi-check-circle-fill' : toast.type === 'danger' ? 'bi bi-x-circle-fill' : 'bi bi-exclamation-triangle-fill'"></i>
              {{ toast.message }}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" @click="remove(toast.id)"></button>
          </div>
        </div>
      </transition-group>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const toasts = ref([])
let nextId = 0

// Exposed so parent can call: toastRef.value.show('message', 'success')
function show(message, type = 'success', duration = 3500) {
  const id = ++nextId
  toasts.value.push({ id, message, type })
  setTimeout(() => remove(id), duration)
}
function remove(id) {
  toasts.value = toasts.value.filter(t => t.id !== id)
}

defineExpose({ show })
</script>

<style scoped>
.toast-fade-enter-active, .toast-fade-leave-active { transition: all 0.3s ease; }
.toast-fade-enter-from { opacity: 0; transform: translateX(40px); }
.toast-fade-leave-to   { opacity: 0; transform: translateX(40px); }
</style>
