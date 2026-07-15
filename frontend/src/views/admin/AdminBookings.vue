<template>
  <Sidebar role="admin">
    <div class="pp-page-header">
      <div>
        <h4><i class="bi bi-journal-check me-2 text-pp"></i>All Bookings</h4>
        <p class="text-muted small mb-0">View and search all user bookings</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="pp-card p-3 mb-3">
      <div class="row g-2 align-items-center">
        <div class="col-md-5">
          <div class="input-group search-input-group">
            <span class="input-group-text"><i class="bi bi-search"></i></span>
            <input v-model="search" type="text" class="form-control" placeholder="Search user or trek name..." @input="fetchBookings" />
          </div>
        </div>
        <div class="col-md-3">
          <select v-model="filterStatus" class="form-select" @change="fetchBookings">
            <option value="">All Statuses</option>
            <option>Booked</option><option>Cancelled</option><option>Completed</option>
          </select>
        </div>
        <div class="col-md-2 text-muted small">{{ bookings.length }} result(s)</div>
      </div>
    </div>

    <LoadingSpinner v-if="loading" />
    <div v-else class="pp-card p-0 overflow-hidden">
      <EmptyState v-if="!bookings.length" icon="bi bi-journal-x" title="No bookings found" message="No bookings match your filters." />
      <div v-else class="table-responsive">
        <table class="table pp-table mb-0">
          <thead>
            <tr><th>User</th><th>Trek</th><th>Location</th><th>Booked On</th><th>Trek Start</th><th>Status</th></tr>
          </thead>
          <tbody>
            <tr v-for="b in bookings" :key="b.id">
              <td>
                <div class="fw-semibold small">{{ b.user_name }}</div>
                <div class="text-muted" style="font-size:0.75rem;">{{ b.user_email }}</div>
              </td>
              <td class="fw-semibold small">{{ b.trek_name }}</td>
              <td class="small text-muted">{{ b.trek_location }}</td>
              <td class="small text-muted">{{ formatDate(b.booking_date) }}</td>
              <td class="small">{{ formatDate(b.trek_start) }}</td>
              <td><StatusBadge :status="b.status" /></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </Sidebar>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Sidebar from '../../components/Sidebar.vue'
import StatusBadge from '../../components/StatusBadge.vue'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import EmptyState from '../../components/EmptyState.vue'
import api from '../../services/api.js'

const bookings     = ref([])
const loading      = ref(true)
const search       = ref('')
const filterStatus = ref('')

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' })
}

async function fetchBookings() {
  loading.value = true
  try {
    const res = await api.get('/admin/bookings', { params:{ q: search.value, status: filterStatus.value } })
    bookings.value = res.data.data
  } finally { loading.value = false }
}

onMounted(fetchBookings)
</script>
