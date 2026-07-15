<template>
  <Sidebar role="staff">
    <LoadingSpinner v-if="loading" />
    <template v-else>
      <div class="pp-page-header">
        <div>
          <h4><i class="bi bi-speedometer2 me-2 text-pp"></i>Staff Dashboard</h4>
          <p class="text-muted small mb-0">Welcome, {{ user?.name }} — manage your assigned treks</p>
        </div>
      </div>

      <!-- Stats -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3">
          <DashboardStatCard icon="bi bi-map-fill" label="Assigned Treks" :value="data.stats?.assigned_treks ?? 0" bg="#d8f3dc" color="#2d6a4f" />
        </div>
        <div class="col-6 col-md-3">
          <DashboardStatCard icon="bi bi-play-circle-fill" label="Active Treks" :value="data.stats?.active_treks ?? 0" bg="#dbeafe" color="#1e40af" />
        </div>
        <div class="col-6 col-md-3">
          <DashboardStatCard icon="bi bi-calendar-event" label="Upcoming Treks" :value="data.stats?.upcoming_treks ?? 0" bg="#fef3c7" color="#92400e" />
        </div>
        <div class="col-6 col-md-3">
          <DashboardStatCard icon="bi bi-people-fill" label="Total Participants" :value="data.stats?.total_participants ?? 0" bg="#ede9fe" color="#5b21b6" />
        </div>
      </div>

      <!-- Trek cards -->
      <div class="pp-card p-4">
        <h6 class="fw-bold mb-3"><i class="bi bi-map me-2 text-pp"></i>My Assigned Treks</h6>
        <div v-if="!data.treks?.length" class="text-center py-4 text-muted">
          <i class="bi bi-inbox fs-1 text-pp d-block mb-2"></i> No treks assigned yet.
        </div>
        <div class="row g-3">
          <div v-for="t in data.treks" :key="t.id" class="col-md-6 col-xl-4">
            <div class="pp-card pp-card-hover p-3 h-100">
              <div class="d-flex justify-content-between align-items-start mb-2">
                <StatusBadge :status="t.status" />
                <DifficultyBadge :difficulty="t.difficulty" />
              </div>
              <h6 class="fw-bold mb-1">{{ t.name }}</h6>
              <p class="text-muted small mb-2"><i class="bi bi-geo-alt me-1"></i>{{ t.location }}</p>
              <div class="row g-1 mb-3">
                <div class="col-6 small text-muted"><i class="bi bi-calendar3 me-1"></i>{{ formatDate(t.start_date) }}</div>
                <div class="col-6 small text-muted"><i class="bi bi-people me-1"></i>{{ t.participant_count }} enrolled</div>
                <div class="col-6 small text-muted"><i class="bi bi-clock me-1"></i>{{ t.duration_days }} day(s)</div>
                <div class="col-6 small text-muted"><i class="bi bi-layers me-1"></i>{{ t.available_slots }}/{{ t.total_slots }} slots</div>
              </div>
              <router-link :to="`/staff/treks/${t.id}`" class="btn btn-pp btn-sm w-100">
                Manage Trek <i class="bi bi-arrow-right ms-1"></i>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </template>
  </Sidebar>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Sidebar from '../../components/Sidebar.vue'
import DashboardStatCard from '../../components/DashboardStatCard.vue'
import StatusBadge from '../../components/StatusBadge.vue'
import DifficultyBadge from '../../components/DifficultyBadge.vue'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import api from '../../services/api.js'

const user    = computed(() => JSON.parse(localStorage.getItem('pp_user') || 'null'))
const loading = ref(true)
const data    = ref({})

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' })
}

onMounted(async () => {
  try {
    const res = await api.get('/staff/dashboard')
    data.value = res.data.data
  } finally { loading.value = false }
})
</script>
