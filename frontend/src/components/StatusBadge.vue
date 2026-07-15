<template>
  <!-- Status badge — trek or booking status -->
  <span class="badge rounded-pill fw-semibold" :class="badgeClass" style="font-size:0.75rem;">
    {{ status }}
  </span>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ status: String })
const badgeClass = computed(() => {
  const map = {
    Open: 'badge-open', Pending: 'badge-pending', Approved: 'badge-approved',
    Closed: 'badge-closed', Completed: 'badge-completed',
    Booked: 'badge-booked', Cancelled: 'badge-cancelled',
  }
  return map[props.status] || 'bg-secondary'
})
</script>
