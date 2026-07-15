<template>
  <Sidebar role="admin">
    <ToastAlert ref="toast" />
    <ConfirmationModal
      :visible="modal.show" :title="modal.title" :message="modal.message"
      :confirm-text="modal.confirmText" :confirm-class="modal.confirmClass"
      :loading="modal.loading" @confirm="modal.action" @cancel="modal.show = false"
    />

    <!-- User Detail Drawer -->
    <Teleport to="body">
      <div v-if="detailUser" class="modal fade show d-block" style="background:rgba(0,0,0,0.5);">
        <div class="modal-dialog modal-dialog-centered modal-lg modal-dialog-scrollable">
          <div class="modal-content border-0 rounded-pp shadow">
            <div class="modal-header">
              <h5 class="modal-title fw-bold"><i class="bi bi-person me-2 text-pp"></i>User Details — {{ detailUser.name }}</h5>
              <button class="btn-close" @click="detailUser=null"></button>
            </div>
            <div class="modal-body">
              <div class="row g-3 mb-4">
                <div class="col-md-6"><strong>Email:</strong> {{ detailUser.email }}</div>
                <div class="col-md-6"><strong>Phone:</strong> {{ detailUser.phone || '—' }}</div>
                <div class="col-md-6"><strong>Joined:</strong> {{ formatDate(detailUser.created_at) }}</div>
                <div class="col-md-6">
                  <strong>Status:</strong>
                  <span v-if="detailUser.is_blacklisted" class="badge badge-cancelled ms-2">Blacklisted</span>
                  <span v-else-if="!detailUser.is_active" class="badge badge-closed ms-2">Inactive</span>
                  <span v-else class="badge badge-open ms-2">Active</span>
                </div>
              </div>
              <h6 class="fw-bold mb-3">Booking History</h6>
              <div class="table-responsive">
                <table class="table table-sm table-hover">
                  <thead class="table-light"><tr><th>Trek</th><th>Location</th><th>Date</th><th>Status</th></tr></thead>
                  <tbody>
                    <tr v-if="!detailBookings.length"><td colspan="4" class="text-center text-muted py-3">No bookings</td></tr>
                    <tr v-for="b in detailBookings" :key="b.id">
                      <td class="small fw-semibold">{{ b.trek_name }}</td>
                      <td class="small text-muted">{{ b.trek_location }}</td>
                      <td class="small">{{ formatDate(b.booking_date) }}</td>
                      <td><StatusBadge :status="b.status" /></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <div class="pp-page-header">
      <div>
        <h4><i class="bi bi-people me-2 text-pp"></i>Manage Users</h4>
        <p class="text-muted small mb-0">View and manage registered trekkers</p>
      </div>
    </div>

    <div class="pp-card p-3 mb-3">
      <div class="input-group search-input-group" style="max-width:380px;">
        <span class="input-group-text"><i class="bi bi-search"></i></span>
        <input v-model="search" type="text" class="form-control" placeholder="Search by name or email..." @input="fetchUsers" />
      </div>
    </div>

    <LoadingSpinner v-if="loading" />

    <div v-else class="pp-card p-0 overflow-hidden">
      <EmptyState v-if="!users.length" icon="bi bi-people" title="No users found" message="No registered users match your search." />
      <div v-else class="table-responsive">
        <table class="table pp-table mb-0">
          <thead>
            <tr><th>Name</th><th>Email</th><th>Phone</th><th>Joined</th><th>Status</th><th class="text-center">Actions</th></tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td class="fw-semibold">{{ u.name }}</td>
              <td class="small text-muted">{{ u.email }}</td>
              <td class="small">{{ u.phone || '—' }}</td>
              <td class="small text-muted">{{ formatDate(u.created_at) }}</td>
              <td>
                <span v-if="u.is_blacklisted" class="badge badge-cancelled">Blacklisted</span>
                <span v-else-if="!u.is_active" class="badge badge-closed">Inactive</span>
                <span v-else class="badge badge-open">Active</span>
              </td>
              <td class="text-center">
                <div class="d-flex gap-1 justify-content-center">
                  <button class="btn btn-sm btn-outline-primary" title="View Details" @click="viewUser(u.id)"><i class="bi bi-eye"></i></button>
                  <button class="btn btn-sm" :class="u.is_active ? 'btn-outline-warning':'btn-outline-success'" @click="toggleActive(u)" :title="u.is_active?'Deactivate':'Activate'">
                    <i :class="u.is_active ? 'bi bi-toggle-on':'bi bi-toggle-off'"></i>
                  </button>
                  <button class="btn btn-sm" :class="u.is_blacklisted?'btn-warning':'btn-outline-danger'" @click="toggleBlacklist(u)" title="Blacklist">
                    <i class="bi bi-slash-circle"></i>
                  </button>
                </div>
              </td>
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
import ConfirmationModal from '../../components/ConfirmationModal.vue'
import ToastAlert from '../../components/ToastAlert.vue'
import api from '../../services/api.js'

const toast   = ref(null)
const users   = ref([])
const loading = ref(true)
const search  = ref('')
const detailUser     = ref(null)
const detailBookings = ref([])
const modal = ref({ show:false, title:'', message:'', confirmText:'', confirmClass:'btn-danger', loading:false, action:()=>{} })

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' })
}

async function fetchUsers() {
  loading.value = true
  try {
    const res = await api.get('/admin/users', { params:{ q: search.value } })
    users.value = res.data.data
  } finally { loading.value = false }
}

async function viewUser(id) {
  const res = await api.get(`/admin/users/${id}`)
  detailUser.value     = res.data.data
  detailBookings.value = res.data.bookings || []
}

async function toggleActive(u) {
  try {
    await api.put(`/admin/users/${u.id}`, { is_active: !u.is_active })
    toast.value.show(`User ${u.is_active?'deactivated':'activated'}.`, 'success')
    fetchUsers()
  } catch(e) { toast.value.show('Failed.', 'danger') }
}

function toggleBlacklist(u) {
  const bl = !u.is_blacklisted
  modal.value = {
    show:true, title: bl?'Blacklist User':'Remove Blacklist',
    message: bl ? `Blacklist "${u.name}"? They will be unable to book treks.` : `Remove blacklist from "${u.name}"?`,
    confirmText: bl?'Blacklist':'Remove', confirmClass: bl?'btn-danger':'btn-warning',
    loading: false,
    action: async () => {
      modal.value.loading = true
      try {
        await api.put(`/admin/users/${u.id}`, { is_blacklisted: bl })
        toast.value.show(`User ${bl?'blacklisted':'removed from blacklist'}.`, bl?'danger':'success')
        modal.value.show = false
        fetchUsers()
      } catch(e) { modal.value.show = false }
    }
  }
}

onMounted(fetchUsers)
</script>
