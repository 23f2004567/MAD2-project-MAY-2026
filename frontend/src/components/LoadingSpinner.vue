<template>
  <div class="pp-loading">
    <div class="pp-spinner"></div>
    <p class="mb-0 text-muted">{{ message }}</p>
  </div>
</template>

<script setup>
defineProps({ message: { type: String, default: 'Loading...' } })
</script>
