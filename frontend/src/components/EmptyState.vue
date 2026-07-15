<template>
  <div class="pp-empty">
    <i :class="icon"></i>
    <h5 class="mb-2">{{ title }}</h5>
    <p class="text-muted mb-0">{{ message }}</p>
    <slot />
  </div>
</template>

<script setup>
defineProps({
  icon:    { type: String, default: 'bi bi-inbox' },
  title:   { type: String, default: 'Nothing here yet' },
  message: { type: String, default: '' },
})
</script>
