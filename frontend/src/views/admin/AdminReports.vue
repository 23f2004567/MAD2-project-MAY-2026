<template>
  <Sidebar role="admin">
    <div class="pp-page-header">
      <div>
        <h4><i class="bi bi-bar-chart-line me-2 text-pp"></i>Analytics & Reports</h4>
        <p class="text-muted small mb-0">Platform insights and booking trends</p>
      </div>
    </div>

    <LoadingSpinner v-if="loading" />

    <template v-else>
      <!-- Summary cards -->
      <div class="row g-3 mb-4">
        <div class="col-md-3">
          <DashboardStatCard icon="bi bi-map-fill" label="Total Treks" :value="data.total_treks" bg="#d8f3dc" color="#2d6a4f" />
        </div>
        <div class="col-md-3">
          <DashboardStatCard icon="bi bi-journal-check" label="Total Bookings" :value="data.total_bookings" bg="#dbeafe" color="#1e40af" />
        </div>
        <div class="col-md-3">
          <DashboardStatCard icon="bi bi-check2-circle" label="Completed Treks" :value="data.completed_treks" bg="#ede9fe" color="#5b21b6" />
        </div>
        <div class="col-md-3">
          <DashboardStatCard icon="bi bi-person-check" label="Active Trekkers" :value="data.active_trekkers" bg="#fef3c7" color="#92400e" />
        </div>
      </div>

      <div class="row g-3 mb-4">
        <!-- Bookings by Month chart -->
        <div class="col-lg-7">
          <div class="pp-card p-4">
            <h6 class="fw-bold mb-3"><i class="bi bi-graph-up me-2 text-pp"></i>Monthly Bookings</h6>
            <canvas ref="bookingChart" height="220"></canvas>
          </div>
        </div>

        <!-- Trek Status distribution chart -->
        <div class="col-lg-5">
          <div class="pp-card p-4">
            <h6 class="fw-bold mb-3"><i class="bi bi-pie-chart me-2 text-pp"></i>Trek Status Distribution</h6>
            <canvas ref="statusChart" height="220"></canvas>
          </div>
        </div>
      </div>

      <div class="row g-3">
        <!-- Popular treks table -->
        <div class="col-lg-7">
          <div class="pp-card p-0 overflow-hidden">
            <div class="px-4 py-3 border-bottom d-flex justify-content-between align-items-center">
              <h6 class="fw-bold mb-0"><i class="bi bi-trophy me-2 text-pp"></i>Popular Treks</h6>
            </div>
            <div class="table-responsive">
              <table class="table table-hover mb-0">
                <thead class="table-light">
                  <tr><th class="px-4">Rank</th><th>Trek Name</th><th>Location</th><th>Bookings</th></tr>
                </thead>
                <tbody>
                  <tr v-for="(t, i) in data.popular_treks" :key="i">
                    <td class="px-4">
                      <span class="badge rounded-pill" :class="i===0?'bg-warning text-dark':i===1?'bg-secondary':'bg-light text-dark border'">
                        #{{ i+1 }}
                      </span>
                    </td>
                    <td class="fw-semibold small">{{ t.name }}</td>
                    <td class="small text-muted">{{ t.location }}</td>
                    <td><span class="badge badge-open">{{ t.bookings }}</span></td>
                  </tr>
                  <tr v-if="!data.popular_treks?.length"><td colspan="4" class="text-center text-muted py-3">No data</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Difficulty distribution -->
        <div class="col-lg-5">
          <div class="pp-card p-4">
            <h6 class="fw-bold mb-3"><i class="bi bi-bar-chart me-2 text-pp"></i>Difficulty Distribution</h6>
            <canvas ref="diffChart" height="220"></canvas>
            <div class="mt-3">
              <div v-for="d in data.difficulty_dist" :key="d.difficulty" class="d-flex justify-content-between align-items-center py-2 border-bottom">
                <DifficultyBadge :difficulty="d.difficulty" />
                <span class="fw-bold">{{ d.count }} trek(s)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </Sidebar>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import Sidebar from '../../components/Sidebar.vue'
import DashboardStatCard from '../../components/DashboardStatCard.vue'
import DifficultyBadge from '../../components/DifficultyBadge.vue'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import api from '../../services/api.js'

Chart.register(...registerables)

const loading     = ref(true)
const data        = ref({})
const bookingChart = ref(null)
const statusChart  = ref(null)
const diffChart    = ref(null)
let chartInstances = []

const GREEN_PALETTE = ['#2d6a4f','#40916c','#52b788','#74c69d','#95d5b2','#b7e4c7','#d8f3dc']

onMounted(async () => {
  try {
    const res = await api.get('/admin/reports')
    data.value = res.data.data
  } catch (e) {
    console.error('Reports API error:', e)
  } finally {
    // Set loading=false FIRST so v-else canvases mount into the DOM
    loading.value = false
    // Then wait for Vue to render the canvases before drawing charts
    await nextTick()
    renderCharts()
  }
})

function renderCharts() {
  // Monthly bookings bar chart
  if (bookingChart.value && data.value.monthly_bookings?.length) {
    new Chart(bookingChart.value, {
      type: 'bar',
      data: {
        labels: data.value.monthly_bookings.map(m => m.month),
        datasets: [{ label: 'Bookings', data: data.value.monthly_bookings.map(m => m.count), backgroundColor: '#40916c', borderRadius: 6 }]
      },
      options: { responsive: true, plugins:{ legend:{display:false} }, scales:{ y:{ beginAtZero:true, ticks:{ stepSize:1 } } } }
    })
  }

  // Trek status doughnut chart
  if (statusChart.value && data.value.trek_status?.length) {
    new Chart(statusChart.value, {
      type: 'doughnut',
      data: {
        labels: data.value.trek_status.map(s => s.status),
        datasets: [{ data: data.value.trek_status.map(s => s.count), backgroundColor: GREEN_PALETTE, borderWidth: 0 }]
      },
      options: { responsive: true, plugins:{ legend:{ position:'bottom' } } }
    })
  }

  // Difficulty bar chart
  if (diffChart.value && data.value.difficulty_dist?.length) {
    new Chart(diffChart.value, {
      type: 'bar',
      data: {
        labels: data.value.difficulty_dist.map(d => d.difficulty),
        datasets: [{ label: 'Treks', data: data.value.difficulty_dist.map(d => d.count), backgroundColor: ['#74c69d','#fbbf24','#f87171'], borderRadius: 6 }]
      },
      options: { responsive: true, plugins:{ legend:{display:false} }, scales:{ y:{ beginAtZero:true, ticks:{ stepSize:1 } } } }
    })
  }
}
</script>
