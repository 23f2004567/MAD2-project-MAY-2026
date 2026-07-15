<template>
  <div class="trek-card">
    <div class="trek-card-header">
      <div class="d-flex justify-content-between align-items-start mb-1">
        <StatusBadge :status="trek.status" />
        <DifficultyBadge :difficulty="trek.difficulty" />
      </div>
      <h5 class="mb-0 mt-2 fw-bold" style="font-size:1rem;">{{ trek.name }}</h5>
      <div class="trek-meta mt-1">
        <i class="bi bi-geo-alt"></i>
        <span>{{ trek.location }}</span>
      </div>
    </div>
    <div class="trek-card-body">
      <div class="row g-2 mb-3">
        <div class="col-6">
          <div class="trek-meta"><i class="bi bi-calendar3"></i> {{ formatDate(trek.start_date) }}</div>
        </div>
        <div class="col-6">
          <div class="trek-meta"><i class="bi bi-clock"></i> {{ trek.duration_days }} day(s)</div>
        </div>
        <div class="col-6">
          <div class="trek-meta"><i class="bi bi-people"></i> {{ trek.available_slots }} slots left</div>
        </div>
        <div class="col-6">
          <div class="trek-meta"><i class="bi bi-layers"></i> {{ trek.total_slots }} total</div>
        </div>
      </div>
      <router-link :to="`/treks/${trek.id}`" class="btn btn-pp w-100">
        View Details <i class="bi bi-arrow-right"></i>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import StatusBadge from './StatusBadge.vue'
import DifficultyBadge from './DifficultyBadge.vue'

defineProps({ trek: { type: Object, required: true } })

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>
