<template>
  <!-- Difficulty badge — Easy/Moderate/Hard -->
  <span class="badge rounded-pill fw-semibold" :class="badgeClass" style="font-size:0.75rem;">
    {{ difficulty }}
  </span>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ difficulty: String })
const badgeClass = computed(() => {
  const map = { Easy: 'badge-easy', Moderate: 'badge-moderate', Hard: 'badge-hard' }
  return map[props.difficulty] || 'bg-secondary'
})
</script>
