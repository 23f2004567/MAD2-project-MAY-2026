<template>
  <Sidebar role="admin">
    <LoadingSpinner v-if="loading" />

    <template v-else>
      <!-- Page header -->
      <div class="pp-page-header">
        <div>
          <h4><i class="bi bi-speedometer2 me-2 text-pp"></i>Admin Dashboard</h4>
          <p class="text-muted small mb-0">Welcome back, {{ user?.name }} — here's your overview</p>
        </div>
        <span class="badge bg-pp px-3 py-2">{{ today }}</span>
      </div>

      <!-- Stat cards -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-xl-3">
          <DashboardStatCard icon="bi bi-map-fill" label="Total Treks" :value="stats.total_treks" bg="#d8f3dc" color="#2d6a4f" />
        </div>
        <div class="col-6 col-xl-3">
          <DashboardStatCard icon="bi bi-people-fill" label="Total Users" :value="stats.total_users" bg="#dbeafe" color="#1e40af" />
        </div>
        <div class="col-6 col-xl-3">
          <DashboardStatCard icon="bi bi-person-badge-fill" label="Staff Members" :value="stats.total_staff" bg="#ede9fe" color="#5b21b6" />
        </div>
        <div class="col-6 col-xl-3">
          <DashboardStatCard icon="bi bi-journal-check" label="Total Bookings" :value="stats.total_bookings" bg="#fef3c7" color="#92400e" />
        </div>
      </div>

      <div class="row g-3">
        <!-- Recent Bookings -->
        <div class="col-lg-7">
          <div class="pp-card p-0 overflow-hidden">
            <div class="d-flex align-items-center justify-content-between px-4 py-3 border-bottom">
              <h6 class="fw-bold mb-0"><i class="bi bi-clock-history me-2 text-pp"></i>Recent Bookings</h6>
              <router-link to="/admin/bookings" class="btn btn-sm btn-pp-outline">View All</router-link>
            </div>
            <div class="table-responsive">
              <table class="table table-hover mb-0">
                <thead style="background:#f8fffe;">
                  <tr>
                    <th class="border-0 text-muted small fw-semibold px-4 py-3">User</th>
                    <th class="border-0 text-muted small fw-semibold py-3">Trek</th>
                    <th class="border-0 text-muted small fw-semibold py-3">Status</th>
                    <th class="border-0 text-muted small fw-semibold py-3">Date</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="!recentBookings.length">
                    <td colspan="4" class="text-center text-muted py-4">No bookings yet</td>
                  </tr>
                  <tr v-for="b in recentBookings" :key="b.id">
                    <td class="px-4">
                      <div class="fw-semibold small">{{ b.user_name }}</div>
                      <div class="text-muted" style="font-size:0.75rem;">{{ b.user_email }}</div>
                    </td>
                    <td class="small">{{ b.trek_name }}</td>
                    <td><StatusBadge :status="b.status" /></td>
                    <td class="small text-muted">{{ formatDate(b.booking_date) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Upcoming Treks & Status summary -->
        <div class="col-lg-5 d-flex flex-column gap-3">
          <!-- Trek status distribution -->
          <div class="pp-card p-4">
            <h6 class="fw-bold mb-3"><i class="bi bi-pie-chart me-2 text-pp"></i>Trek Status</h6>
            <div class="d-flex flex-column gap-2">
              <div v-for="(count, status) in statusCounts" :key="status" class="d-flex align-items-center justify-content-between">
                <StatusBadge :status="status" />
                <span class="fw-bold">{{ count }}</span>
              </div>
              <div v-if="!Object.keys(statusCounts).length" class="text-muted small">No data</div>
            </div>
          </div>

          <!-- Upcoming treks -->
          <div class="pp-card p-4 flex-grow-1">
            <h6 class="fw-bold mb-3"><i class="bi bi-calendar-event me-2 text-pp"></i>Upcoming Treks</h6>
            <div v-if="!upcomingTreks.length" class="text-muted small">No upcoming treks</div>
            <div v-for="t in upcomingTreks" :key="t.id" class="d-flex align-items-center justify-content-between py-2 border-bottom">
              <div>
                <div class="fw-semibold small">{{ t.name }}</div>
                <div class="text-muted" style="font-size:0.75rem;"><i class="bi bi-geo-alt me-1"></i>{{ t.location }}</div>
              </div>
              <div class="text-end">
                <div class="small fw-semibold text-pp">{{ formatDate(t.start_date) }}</div>
                <DifficultyBadge :difficulty="t.difficulty" />
              </div>
            </div>
          </div>
        </div>

        <!-- Popular Treks -->
        <div class="col-12">
          <div class="pp-card p-4">
            <h6 class="fw-bold mb-3"><i class="bi bi-trophy me-2 text-pp"></i>Popular Treks</h6>
            <div class="row g-3">
              <div v-for="item in popularTreks" :key="item.trek.id" class="col-md-4">
                <div class="d-flex align-items-center gap-3 p-3 rounded-3" style="background:#f8fffe;border:1px solid #e8f0eb;">
                  <div class="icon-box flex-shrink-0" style="background:#d8f3dc;width:42px;height:42px;border-radius:10px;display:flex;align-items:center;justify-content:center;">
                    <i class="bi bi-mountain text-pp"></i>
                  </div>
                  <div class="flex-grow-1 overflow-hidden">
                    <div class="fw-semibold small text-truncate">{{ item.trek.name }}</div>
                    <div class="text-muted" style="font-size:0.75rem;">{{ item.booking_count }} booking(s)</div>
                  </div>
                </div>
              </div>
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
const stats          = ref({ total_treks: 0, total_users: 0, total_staff: 0, total_bookings: 0 })
const recentBookings = ref([])
const upcomingTreks  = ref([])
const popularTreks   = ref([])
const statusCounts   = ref({})
const today = new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
}

onMounted(async () => {
  try {
    const res = await api.get('/admin/dashboard')
    const d   = res.data.data
    stats.value          = d.stats
    recentBookings.value = d.recent_bookings || []
    upcomingTreks.value  = d.upcoming_treks  || []
    popularTreks.value   = d.popular_treks   || []
    statusCounts.value   = d.status_counts   || {}
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>
