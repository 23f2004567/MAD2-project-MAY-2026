<template>
  <div>
    <Navbar />
    <div class="container py-4" style="max-width:860px; margin:auto;">
      <LoadingSpinner v-if="loading" />

      <template v-else-if="trek">
        <ToastAlert ref="toast" />
        <ConfirmationModal
          :visible="confirmBook"
          title="Book This Trek"
          :message="`Book '${trek.name}' starting ${formatDate(trek.start_date)}? This will use 1 available slot.`"
          confirm-text="Confirm Booking"
          confirm-class="btn-pp"
          icon="bi bi-calendar-check text-pp"
          :loading="bookLoading"
          @confirm="bookTrek"
          @cancel="confirmBook = false"
        />

        <button class="btn btn-sm btn-outline-secondary mb-3" @click="$router.back()">
          <i class="bi bi-arrow-left me-1"></i> Back
        </button>

        <!-- Trek header -->
        <div class="rounded-pp mb-4 p-4 text-white" style="background:linear-gradient(135deg, var(--pp-green-dark), var(--pp-green));">
          <div class="d-flex justify-content-between align-items-start flex-wrap gap-2 mb-2">
            <StatusBadge :status="trek.status" />
            <DifficultyBadge :difficulty="trek.difficulty" />
          </div>
          <h2 class="fw-bold mb-1">{{ trek.name }}</h2>
          <p class="mb-0" style="opacity:0.85;"><i class="bi bi-geo-alt me-1"></i>{{ trek.location }}</p>
        </div>

        <div class="row g-3">
          <!-- Details -->
          <div class="col-md-8">
            <div class="pp-card p-4 mb-3">
              <h5 class="fw-bold mb-3">About this Trek</h5>
              <p class="text-muted">{{ trek.description || 'No description provided.' }}</p>
            </div>
            <div class="pp-card p-4">
              <h5 class="fw-bold mb-3">Trek Details</h5>
              <div class="row g-3">
                <div class="col-sm-6">
                  <div class="d-flex align-items-center gap-2 p-3 rounded-3" style="background:#f8fffe;border:1px solid #e8f0eb;">
                    <i class="bi bi-calendar3 fs-4 text-pp"></i>
                    <div><div class="small text-muted">Start Date</div><div class="fw-semibold">{{ formatDate(trek.start_date) }}</div></div>
                  </div>
                </div>
                <div class="col-sm-6">
                  <div class="d-flex align-items-center gap-2 p-3 rounded-3" style="background:#f8fffe;border:1px solid #e8f0eb;">
                    <i class="bi bi-calendar-check fs-4 text-pp"></i>
                    <div><div class="small text-muted">End Date</div><div class="fw-semibold">{{ formatDate(trek.end_date) }}</div></div>
                  </div>
                </div>
                <div class="col-sm-6">
                  <div class="d-flex align-items-center gap-2 p-3 rounded-3" style="background:#f8fffe;border:1px solid #e8f0eb;">
                    <i class="bi bi-clock fs-4 text-pp"></i>
                    <div><div class="small text-muted">Duration</div><div class="fw-semibold">{{ trek.duration_days }} day(s)</div></div>
                  </div>
                </div>
                <div class="col-sm-6">
                  <div class="d-flex align-items-center gap-2 p-3 rounded-3" style="background:#f8fffe;border:1px solid #e8f0eb;">
                    <i class="bi bi-layers fs-4 text-pp"></i>
                    <div><div class="small text-muted">Difficulty</div><div class="fw-semibold">{{ trek.difficulty }}</div></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Booking sidebar -->
          <div class="col-md-4">
            <div class="pp-card p-4 position-sticky" style="top:80px;">
              <h6 class="fw-bold mb-3">Slot Availability</h6>
              <div class="mb-3">
                <div class="d-flex justify-content-between mb-1">
                  <span class="small text-muted">Available</span>
                  <span class="fw-bold text-pp">{{ trek.available_slots }}</span>
                </div>
                <div class="progress" style="height:8px;border-radius:4px;">
                  <div class="progress-bar bg-pp" :style="{ width: slotPercent + '%' }"></div>
                </div>
                <div class="d-flex justify-content-between mt-1">
                  <span class="small text-muted">0</span>
                  <span class="small text-muted">{{ trek.total_slots }} total</span>
                </div>
              </div>

              <div v-if="bookingError" class="alert alert-danger py-2 small mb-3">
                <i class="bi bi-exclamation-circle me-1"></i>{{ bookingError }}
              </div>
              <div v-if="bookingSuccess" class="alert alert-success py-2 small mb-3">
                <i class="bi bi-check-circle me-1"></i>{{ bookingSuccess }}
              </div>

              <button
                class="btn btn-pp w-100 py-2"
                :disabled="trek.status !== 'Open' || trek.available_slots <= 0"
                @click="confirmBook = true"
              >
                <i class="bi bi-calendar-plus me-2"></i>
                <template v-if="trek.status !== 'Open'">Not Available</template>
                <template v-else-if="trek.available_slots <= 0">Fully Booked</template>
                <template v-else>Book This Trek</template>
              </button>

              <div v-if="trek.assigned_staff" class="mt-3 pt-3 border-top text-muted small">
                <i class="bi bi-person-badge me-1 text-pp"></i>
                Led by <strong>{{ trek.assigned_staff }}</strong>
              </div>
            </div>
          </div>
        </div>
      </template>

      <EmptyState v-else icon="bi bi-exclamation-circle" title="Trek not found" message="This trek may no longer be available." />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from '../../components/Navbar.vue'
import StatusBadge from '../../components/StatusBadge.vue'
import DifficultyBadge from '../../components/DifficultyBadge.vue'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import EmptyState from '../../components/EmptyState.vue'
import ConfirmationModal from '../../components/ConfirmationModal.vue'
import ToastAlert from '../../components/ToastAlert.vue'
import api from '../../services/api.js'

const route          = useRoute()
const toast          = ref(null)
const trek           = ref(null)
const loading        = ref(true)
const confirmBook    = ref(false)
const bookLoading    = ref(false)
const bookingError   = ref('')
const bookingSuccess = ref('')

const slotPercent = computed(() => {
  if (!trek.value) return 0
  return Math.round((trek.value.available_slots / trek.value.total_slots) * 100)
})

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN', { day:'2-digit', month:'long', year:'numeric' })
}

async function fetchTrek() {
  try {
    const res = await api.get(`/treks/${route.params.id}`)
    trek.value = res.data.data
  } catch { trek.value = null }
  finally { loading.value = false }
}

async function bookTrek() {
  bookLoading.value = true
  bookingError.value = ''
  bookingSuccess.value = ''
  try {
    await api.post('/user/bookings', { trek_id: trek.value.id })
    confirmBook.value = false
    bookingSuccess.value = 'Trek booked successfully! Check your bookings.'
    trek.value.available_slots -= 1
    toast.value?.show('Trek booked successfully!', 'success')
  } catch(e) {
    confirmBook.value = false
    bookingError.value = e.response?.data?.message || 'Booking failed.'
    toast.value?.show(bookingError.value, 'danger')
  } finally { bookLoading.value = false }
}

onMounted(fetchTrek)
</script>
