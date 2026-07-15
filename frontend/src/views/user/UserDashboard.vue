<template>
  <div>
    <Navbar />
    <div class="container-fluid py-4 px-3 px-md-4" style="max-width:1200px; margin:auto;">
      <LoadingSpinner v-if="loading" />

      <template v-else>
        <!-- Welcome banner -->
        <div class="rounded-pp mb-4 p-4" style="background:linear-gradient(135deg, var(--pp-green-dark), var(--pp-green)); color:white;">
          <div class="d-flex align-items-center justify-content-between flex-wrap gap-3">
            <div>
              <h4 class="fw-bold mb-1">Welcome back, {{ user?.name }}! 🏔️</h4>
              <p class="mb-0" style="opacity:0.85;">Ready for your next adventure? Explore. Book. Trek.</p>
            </div>
            <router-link to="/treks" class="btn btn-light fw-semibold px-4" style="color:var(--pp-green-dark);">
              <i class="bi bi-map me-2"></i>Browse Treks
            </router-link>
          </div>
        </div>

        <!-- Stat cards -->
        <div class="row g-3 mb-4">
          <div class="col-6 col-md-3">
            <DashboardStatCard icon="bi bi-map-fill" label="Open Treks" :value="data.stats?.available_treks ?? 0" bg="#d8f3dc" color="#2d6a4f" />
          </div>
          <div class="col-6 col-md-3">
            <DashboardStatCard icon="bi bi-calendar-check" label="Upcoming" :value="data.stats?.upcoming_bookings ?? 0" bg="#dbeafe" color="#1e40af" />
          </div>
          <div class="col-6 col-md-3">
            <DashboardStatCard icon="bi bi-trophy-fill" label="Completed" :value="data.stats?.completed_treks ?? 0" bg="#ede9fe" color="#5b21b6" />
          </div>
          <div class="col-6 col-md-3">
            <DashboardStatCard icon="bi bi-journal-check" label="Total Bookings" :value="data.stats?.total_bookings ?? 0" bg="#fef3c7" color="#92400e" />
          </div>
        </div>

        <div class="row g-4">
          <!-- Upcoming bookings -->
          <div class="col-lg-5">
            <div class="pp-card p-4">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h6 class="fw-bold mb-0"><i class="bi bi-calendar-event me-2 text-pp"></i>Upcoming Treks</h6>
                <router-link to="/bookings" class="btn btn-sm btn-pp-outline">View All</router-link>
              </div>
              <div v-if="!data.upcoming_bookings?.length" class="text-center py-3 text-muted small">
                <i class="bi bi-calendar-x d-block fs-2 mb-2"></i> No upcoming bookings.
                <router-link to="/treks" class="btn btn-pp btn-sm mt-2">Explore Treks</router-link>
              </div>
              <div v-for="b in data.upcoming_bookings" :key="b.id" class="d-flex gap-3 py-3 border-bottom">
                <div class="icon-box flex-shrink-0" style="width:44px;height:44px;border-radius:12px;background:#d8f3dc;display:flex;align-items:center;justify-content:center;">
                  <i class="bi bi-mountain text-pp"></i>
                </div>
                <div class="flex-grow-1">
                  <div class="fw-semibold small">{{ b.trek_name }}</div>
                  <div class="text-muted" style="font-size:0.75rem;"><i class="bi bi-geo-alt me-1"></i>{{ b.trek_location }}</div>
                  <div class="text-muted" style="font-size:0.75rem;"><i class="bi bi-calendar3 me-1"></i>{{ formatDate(b.trek_start) }}</div>
                </div>
                <StatusBadge :status="b.status" />
              </div>
            </div>
          </div>

          <!-- Recommended treks -->
          <div class="col-lg-7">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h6 class="fw-bold mb-0"><i class="bi bi-compass me-2 text-pp"></i>Recommended Treks</h6>
              <router-link to="/treks" class="btn btn-sm btn-pp-outline">Browse All</router-link>
            </div>
            <div v-if="!data.recommended_treks?.length" class="text-center py-4 text-muted">
              <i class="bi bi-map fs-1 d-block mb-2 text-pp"></i>No open treks available right now.
            </div>
            <div class="row g-3">
              <div v-for="t in data.recommended_treks?.slice(0,4)" :key="t.id" class="col-md-6">
                <TrekCard :trek="t" />
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Navbar from '../../components/Navbar.vue'
import DashboardStatCard from '../../components/DashboardStatCard.vue'
import TrekCard from '../../components/TrekCard.vue'
import StatusBadge from '../../components/StatusBadge.vue'
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
    const res = await api.get('/user/dashboard')
    data.value = res.data.data
  } finally { loading.value = false }
})
</script>
