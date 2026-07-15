<template>
  <!-- stat card used on all dashboards -->
  <div class="stat-card">
    <div class="icon-box" :style="{ background: bg }">
      <i :class="icon" :style="{ color: color }"></i>
    </div>
    <div>
      <div class="value">{{ value }}</div>
      <div class="label">{{ label }}</div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  icon:  { type: String, required: true },
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  bg:    { type: String, default: '#d8f3dc' },
  color: { type: String, default: '#2d6a4f' },
})
</script>
