<template>
  <Sidebar role="staff">
    <div class="pp-page-header">
      <div>
        <h4><i class="bi bi-map me-2 text-pp"></i>My Assigned Treks</h4>
        <p class="text-muted small mb-0">All treks assigned to you</p>
      </div>
    </div>
    <LoadingSpinner v-if="loading" />
    <div v-else>
      <EmptyState v-if="!treks.length" icon="bi bi-map" title="No treks assigned" message="Contact the admin to get a trek assigned." />
      <div v-else class="row g-3">
        <div v-for="t in treks" :key="t.id" class="col-md-6 col-xl-4">
          <div class="trek-card">
            <div class="trek-card-header">
              <div class="d-flex justify-content-between">
                <StatusBadge :status="t.status" />
                <DifficultyBadge :difficulty="t.difficulty" />
              </div>
              <h5 class="mt-2 mb-0 fw-bold" style="font-size:1rem;">{{ t.name }}</h5>
              <p class="trek-meta mt-1"><i class="bi bi-geo-alt me-1"></i>{{ t.location }}</p>
            </div>
            <div class="trek-card-body">
              <div class="row g-2 mb-3">
                <div class="col-6 trek-meta"><i class="bi bi-calendar3 me-1"></i>{{ formatDate(t.start_date) }}</div>
                <div class="col-6 trek-meta"><i class="bi bi-clock me-1"></i>{{ t.duration_days }} day(s)</div>
                <div class="col-6 trek-meta"><i class="bi bi-people me-1"></i>{{ t.participant_count }} enrolled</div>
                <div class="col-6 trek-meta"><i class="bi bi-layers me-1"></i>{{ t.available_slots }}/{{ t.total_slots }}</div>
              </div>
              <router-link :to="`/staff/treks/${t.id}`" class="btn btn-pp w-100 btn-sm">
                Manage <i class="bi bi-arrow-right ms-1"></i>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Sidebar>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Sidebar from '../../components/Sidebar.vue'
import StatusBadge from '../../components/StatusBadge.vue'
import DifficultyBadge from '../../components/DifficultyBadge.vue'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import EmptyState from '../../components/EmptyState.vue'
import api from '../../services/api.js'

const treks   = ref([])
const loading = ref(true)

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' })
}

onMounted(async () => {
  try { const res = await api.get('/staff/treks'); treks.value = res.data.data }
  finally { loading.value = false }
})
</script>
