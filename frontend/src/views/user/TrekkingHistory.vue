<template>
  <div>
    <Navbar />
    <div class="container py-4" style="max-width:1000px; margin:auto;">
      <ToastAlert ref="toast" />

      <div class="pp-page-header">
        <div>
          <h4><i class="bi bi-clock-history me-2 text-pp"></i>Trekking History</h4>
          <p class="text-muted small mb-0">Your completed and cancelled treks</p>
        </div>
        <button class="btn btn-pp" @click="startExport" :disabled="exportState === 'loading'">
          <span v-if="exportState === 'loading'" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="bi bi-download me-2"></i>
          {{ exportState === 'loading' ? 'Generating...' : 'Export History CSV' }}
        </button>
      </div>

      <div v-if="exportState === 'ready'" class="alert alert-success d-flex align-items-center justify-content-between mb-3">
        <span><i class="bi bi-check-circle me-2"></i>Your CSV is ready!</span>
        <button @click="downloadCSV" class="btn btn-success btn-sm" :disabled="downloading">
          <span v-if="downloading" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="bi bi-download me-1"></i>Download CSV
        </button>
      </div>
      <div v-if="exportState === 'polling'" class="alert alert-info mb-3">
        <span class="spinner-border spinner-border-sm me-2"></span>Generating your CSV export in the background...
      </div>
      <div v-if="exportState === 'error'" class="alert alert-danger mb-3">
        <i class="bi bi-x-circle me-2"></i>Export failed. Please try again.
      </div>

      <LoadingSpinner v-if="loading" />

      <template v-else>
        <EmptyState v-if="!history.length" icon="bi bi-clock-history" title="No history yet"
          message="Completed and cancelled treks will appear here." />

        <div v-else class="pp-card p-0 overflow-hidden">
          <div class="table-responsive">
            <table class="table pp-table mb-0">
              <thead>
                <tr><th>Trek</th><th>Location</th><th>Trek Dates</th><th>Booked On</th><th>Status</th></tr>
              </thead>
              <tbody>
                <tr v-for="b in history" :key="b.id">
                  <td class="fw-semibold small">{{ b.trek_name }}</td>
                  <td class="small text-muted">{{ b.trek_location }}</td>
                  <td class="small">{{ formatDate(b.trek_start) }} — {{ formatDate(b.trek_end) }}</td>
                  <td class="small text-muted">{{ formatDate(b.booking_date) }}</td>
                  <td><StatusBadge :status="b.status" /></td>
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
import { ref, onMounted, onUnmounted } from 'vue'
import Navbar from '../../components/Navbar.vue'
import StatusBadge from '../../components/StatusBadge.vue'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import EmptyState from '../../components/EmptyState.vue'
import ToastAlert from '../../components/ToastAlert.vue'
import api from '../../services/api.js'

const toast          = ref(null)
const history        = ref([])
const loading        = ref(true)
// Export states: idle | loading | polling | ready | error
const exportState    = ref('idle')
const exportFilename = ref('')
const exportTaskId   = ref('')
const downloading    = ref(false)
let pollInterval     = null

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' })
}

async function fetchHistory() {
  loading.value = true
  try { const res = await api.get('/user/history'); history.value = res.data.data }
  finally { loading.value = false }
}

// Async CSV Export
async function startExport() {
  exportState.value = 'loading'
  exportFilename.value = ''
  try {
    // Queue Celery task, get task_id back immediately
    const res = await api.post('/user/export-history')
    exportTaskId.value = res.data.task_id
    exportState.value = 'polling'
    // Poll every 2 seconds for task completion
    pollInterval = setInterval(pollExportStatus, 2000)
  } catch {
    exportState.value = 'error'
  }
}

async function pollExportStatus() {
  try {
    const res = await api.get(`/user/export-status/${exportTaskId.value}`)
    if (res.data.state === 'SUCCESS') {
      clearInterval(pollInterval)
      exportFilename.value = res.data.filename
      exportState.value = 'ready'
      toast.value.show('Your CSV export is ready!', 'success')
    } else if (res.data.state === 'FAILURE') {
      clearInterval(pollInterval)
      exportState.value = 'error'
    }
  } catch {
    clearInterval(pollInterval)
    exportState.value = 'error'
  }
}

async function downloadCSV() {
  downloading.value = true
  try {
    const res = await api.get(`/user/export-download/${exportFilename.value}`, {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', exportFilename.value)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (err) {
    if (toast.value) {
      toast.value.show('Failed to download CSV.', 'danger')
    }
  } finally {
    downloading.value = false
  }
}

onMounted(fetchHistory)
onUnmounted(() => { if (pollInterval) clearInterval(pollInterval) })
</script>
