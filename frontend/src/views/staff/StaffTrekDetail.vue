<template>
  <Sidebar role="staff">
    <ToastAlert ref="toast" />

    <LoadingSpinner v-if="loading" />

    <template v-else-if="trek">
      <div class="pp-page-header">
        <div>
          <router-link to="/staff/treks" class="btn btn-sm btn-outline-secondary mb-2">
            <i class="bi bi-arrow-left me-1"></i> Back
          </router-link>
          <h4 class="mb-0">{{ trek.name }}</h4>
          <p class="text-muted small mb-0"><i class="bi bi-geo-alt me-1"></i>{{ trek.location }}</p>
        </div>
        <div class="d-flex gap-2 align-items-center flex-wrap">
          <StatusBadge :status="trek.status" />
          <DifficultyBadge :difficulty="trek.difficulty" />
        </div>
      </div>

      <div class="row g-3">
        <!-- Trek info -->
        <div class="col-lg-4">
          <div class="pp-card p-4">
            <h6 class="fw-bold mb-3">Trek Information</h6>
            <table class="table table-sm table-borderless mb-3">
              <tbody>
                <tr><td class="text-muted small fw-semibold">Start</td><td class="small">{{ formatDate(trek.start_date) }}</td></tr>
                <tr><td class="text-muted small fw-semibold">End</td><td class="small">{{ formatDate(trek.end_date) }}</td></tr>
                <tr><td class="text-muted small fw-semibold">Duration</td><td class="small">{{ trek.duration_days }} day(s)</td></tr>
                <tr><td class="text-muted small fw-semibold">Total Slots</td><td class="small">{{ trek.total_slots }}</td></tr>
                <tr><td class="text-muted small fw-semibold">Available</td><td class="small fw-bold text-pp">{{ trek.available_slots }}</td></tr>
                <tr><td class="text-muted small fw-semibold">Enrolled</td><td class="small">{{ trek.participant_count }}</td></tr>
              </tbody>
            </table>

            <hr />
            <!-- Update controls for staff -->
            <h6 class="fw-bold mb-3">Update Trek</h6>
            <div class="mb-3">
              <label class="form-label">Status</label>
              <select v-model="updateForm.status" class="form-select form-select-sm">
                <option v-for="s in allowedStatuses" :key="s">{{ s }}</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">Available Slots</label>
              <input v-model.number="updateForm.available_slots" type="number" :min="0" :max="trek.total_slots" class="form-control form-control-sm" />
            </div>
            <button class="btn btn-pp w-100 btn-sm" @click="updateTrek" :disabled="updateLoading">
              <span v-if="updateLoading" class="spinner-border spinner-border-sm me-2"></span>
              Save Changes
            </button>
          </div>
        </div>

        <!-- Participants table -->
        <div class="col-lg-8">
          <div class="pp-card p-0 overflow-hidden">
            <div class="px-4 py-3 border-bottom d-flex justify-content-between align-items-center">
              <h6 class="fw-bold mb-0"><i class="bi bi-people me-2 text-pp"></i>Participants ({{ participants.length }})</h6>
            </div>
            <LoadingSpinner v-if="pLoading" />
            <div v-else class="table-responsive">
              <EmptyState v-if="!participants.length" icon="bi bi-people" title="No participants yet" message="Users who book this trek will appear here." />
              <table v-else class="table pp-table mb-0">
                <thead>
                  <tr><th>Name</th><th>Email</th><th>Phone</th><th>Booked</th><th>Status</th><th class="text-center">Action</th></tr>
                </thead>
                <tbody>
                  <tr v-for="p in participants" :key="p.booking_id">
                    <td class="fw-semibold small">{{ p.user_name }}</td>
                    <td class="small text-muted">{{ p.user_email }}</td>
                    <td class="small">{{ p.user_phone || '—' }}</td>
                    <td class="small text-muted">{{ formatDate(p.booking_date) }}</td>
                    <td><StatusBadge :status="p.booking_status" /></td>
                    <td class="text-center">
                      <button
                        v-if="p.booking_status === 'Booked'"
                        class="btn btn-sm btn-outline-success"
                        @click="markComplete(p.booking_id)"
                        title="Mark as Completed"
                      >
                        <i class="bi bi-check2-circle me-1"></i>Complete
                      </button>
                      <span v-else class="text-muted small">—</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </template>

    <EmptyState v-else icon="bi bi-exclamation-circle" title="Trek not found" message="This trek may not be assigned to you." />
  </Sidebar>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from '../../components/Sidebar.vue'
import StatusBadge from '../../components/StatusBadge.vue'
import DifficultyBadge from '../../components/DifficultyBadge.vue'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import EmptyState from '../../components/EmptyState.vue'
import ToastAlert from '../../components/ToastAlert.vue'
import api from '../../services/api.js'

const route  = useRoute()
const toast  = ref(null)
const trek   = ref(null)
const loading = ref(true)
const pLoading = ref(false)
const participants = ref([])
const updateLoading = ref(false)
const updateForm = ref({ status: '', available_slots: 0 })

// Status transitions staff is allowed to make
const allowedStatuses = ['Approved','Open','Closed','Completed']

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' })
}

async function fetchTrek() {
  loading.value = true
  try {
    const res = await api.get(`/staff/treks/${route.params.id}`)
    trek.value = res.data.data
    updateForm.value = { status: trek.value.status, available_slots: trek.value.available_slots }
    fetchParticipants()
  } catch { trek.value = null }
  finally { loading.value = false }
}

async function fetchParticipants() {
  pLoading.value = true
  try {
    const res = await api.get(`/staff/treks/${route.params.id}/participants`)
    participants.value = res.data.data
  } finally { pLoading.value = false }
}

async function updateTrek() {
  updateLoading.value = true
  try {
    await api.put(`/staff/treks/${route.params.id}`, updateForm.value)
    toast.value.show('Trek updated successfully.', 'success')
    fetchTrek()
  } catch(e) {
    toast.value.show(e.response?.data?.message || 'Update failed.', 'danger')
  } finally { updateLoading.value = false }
}

async function markComplete(bookingId) {
  try {
    await api.put(`/staff/bookings/${bookingId}/complete`)
    toast.value.show('Participant marked as completed.', 'success')
    fetchParticipants()
  } catch(e) {
    toast.value.show(e.response?.data?.message || 'Failed.', 'danger')
  }
}

onMounted(fetchTrek)
</script>
