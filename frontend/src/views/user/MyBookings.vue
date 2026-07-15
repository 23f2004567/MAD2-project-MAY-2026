<template>
  <div>
    <Navbar />
    <div class="container py-4" style="max-width:1000px; margin:auto;">
      <ToastAlert ref="toast" />
      <ConfirmationModal
        :visible="modal.show" title="Cancel Booking"
        :message="`Cancel your booking for '${modal.trekName}'? One slot will be restored.`"
        confirm-text="Cancel Booking" confirm-class="btn-danger"
        icon="bi bi-x-circle text-danger"
        :loading="modal.loading"
        @confirm="cancelBooking"
        @cancel="modal.show=false"
      />

      <div class="pp-page-header">
        <div>
          <h4><i class="bi bi-journal-check me-2 text-pp"></i>My Bookings</h4>
          <p class="text-muted small mb-0">Your active and past trek bookings</p>
        </div>
      </div>

      <LoadingSpinner v-if="loading" />

      <template v-else>
        <EmptyState v-if="!bookings.length" icon="bi bi-journal-x" title="No bookings yet"
          message="Book your first trek to see it here.">
          <router-link to="/treks" class="btn btn-pp mt-3">Browse Treks</router-link>
        </EmptyState>

        <div v-else class="pp-card p-0 overflow-hidden">
          <div class="table-responsive">
            <table class="table pp-table mb-0">
              <thead>
                <tr><th>Trek</th><th>Location</th><th>Booked On</th><th>Trek Dates</th><th>Status</th><th class="text-center">Action</th></tr>
              </thead>
              <tbody>
                <tr v-for="b in bookings" :key="b.id">
                  <td class="fw-semibold small">{{ b.trek_name }}</td>
                  <td class="small text-muted"><i class="bi bi-geo-alt me-1"></i>{{ b.trek_location }}</td>
                  <td class="small text-muted">{{ formatDate(b.booking_date) }}</td>
                  <td class="small">
                    {{ formatDate(b.trek_start) }}<span class="text-muted"> → </span>{{ formatDate(b.trek_end) }}
                  </td>
                  <td><StatusBadge :status="b.status" /></td>
                  <td class="text-center">
                    <button
                      v-if="b.status === 'Booked'"
                      class="btn btn-sm btn-outline-danger"
                      @click="openCancel(b)"
                    >
                      <i class="bi bi-x-circle me-1"></i>Cancel
                    </button>
                    <span v-else class="text-muted small">—</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '../../components/Navbar.vue'
import StatusBadge from '../../components/StatusBadge.vue'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import EmptyState from '../../components/EmptyState.vue'
import ConfirmationModal from '../../components/ConfirmationModal.vue'
import ToastAlert from '../../components/ToastAlert.vue'
import api from '../../services/api.js'

const toast    = ref(null)
const bookings = ref([])
const loading  = ref(true)
const modal    = ref({ show:false, trekName:'', bookingId:null, loading:false })

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' })
}

async function fetchBookings() {
  loading.value = true
  try { const res = await api.get('/user/bookings'); bookings.value = res.data.data }
  finally { loading.value = false }
}

function openCancel(b) {
  modal.value = { show:true, trekName: b.trek_name, bookingId: b.id, loading:false }
}

async function cancelBooking() {
  modal.value.loading = true
  try {
    await api.put(`/user/bookings/${modal.value.bookingId}/cancel`)
    toast.value.show('Booking cancelled successfully.', 'success')
    modal.value.show = false
    fetchBookings()
  } catch(e) {
    toast.value.show(e.response?.data?.message || 'Cancellation failed.', 'danger')
    modal.value.show = false
  }
}

onMounted(fetchBookings)
</script>
