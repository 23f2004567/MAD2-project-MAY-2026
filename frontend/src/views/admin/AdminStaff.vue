<template>
  <Sidebar role="admin">
    <ToastAlert ref="toast" />
    <ConfirmationModal
      :visible="modal.show" :title="modal.title" :message="modal.message"
      :confirm-text="modal.confirmText" :confirm-class="modal.confirmClass"
      :loading="modal.loading" @confirm="modal.action" @cancel="modal.show = false"
    />

    <!-- Staff Form Modal -->
    <Teleport to="body">
      <div v-if="formModal" class="modal fade show d-block" style="background:rgba(0,0,0,0.5);">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content border-0 rounded-pp shadow">
            <div class="modal-header">
              <h5 class="modal-title fw-bold">
                <i class="bi bi-person-badge me-2 text-pp"></i>{{ editingStaff ? 'Edit Staff' : 'Add Staff Member' }}
              </h5>
              <button class="btn-close" @click="formModal=false"></button>
            </div>
            <div class="modal-body">
              <div v-if="formError" class="alert alert-danger py-2 small">{{ formError }}</div>
              <div class="row g-3">
                <div class="col-12">
                  <label class="form-label">Full Name *</label>
                  <input v-model="form.name" type="text" class="form-control" />
                </div>
                <div class="col-12" v-if="!editingStaff">
                  <label class="form-label">Email Address *</label>
                  <input v-model="form.email" type="email" class="form-control" />
                </div>
                <div class="col-12">
                  <label class="form-label">Phone</label>
                  <input v-model="form.phone" type="tel" class="form-control" />
                </div>
                <div class="col-12">
                  <label class="form-label">{{ editingStaff ? 'New Password (leave blank to keep)' : 'Password *' }}</label>
                  <input v-model="form.password" type="password" class="form-control" :placeholder="editingStaff ? 'Leave blank to keep current' : 'Min. 6 characters'" />
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn btn-outline-secondary" @click="formModal=false">Cancel</button>
              <button class="btn btn-pp px-4" @click="submitForm" :disabled="formLoading">
                <span v-if="formLoading" class="spinner-border spinner-border-sm me-2"></span>
                {{ editingStaff ? 'Save Changes' : 'Create Staff' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Page Header -->
    <div class="pp-page-header">
      <div>
        <h4><i class="bi bi-person-badge me-2 text-pp"></i>Manage Staff</h4>
        <p class="text-muted small mb-0">Create and manage trek staff accounts</p>
      </div>
      <button class="btn btn-pp" @click="openCreate">
        <i class="bi bi-plus-lg me-2"></i>Add Staff
      </button>
    </div>

    <!-- Search -->
    <div class="pp-card p-3 mb-3">
      <div class="input-group search-input-group" style="max-width:380px;">
        <span class="input-group-text"><i class="bi bi-search"></i></span>
        <input v-model="search" type="text" class="form-control" placeholder="Search staff..." @input="fetchStaff" />
      </div>
    </div>

    <LoadingSpinner v-if="loading" />

    <div v-else class="pp-card p-0 overflow-hidden">
      <EmptyState v-if="!staff.length" icon="bi bi-person-badge" title="No staff members" message="Add your first trek staff member." />
      <div v-else class="table-responsive">
        <table class="table pp-table mb-0">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Assigned Treks</th>
              <th>Status</th>
              <th class="text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in staff" :key="s.id">
              <td class="fw-semibold">{{ s.name }}</td>
              <td class="small text-muted">{{ s.email }}</td>
              <td class="small">{{ s.phone || '—' }}</td>
              <td class="small">
                <span v-if="s.assigned_treks?.length" class="d-flex flex-wrap gap-1">
                  <span v-for="t in s.assigned_treks" :key="t.id" class="badge bg-light text-dark border small">{{ t.name }}</span>
                </span>
                <span v-else class="text-muted">—</span>
              </td>
              <td>
                <span v-if="s.is_blacklisted" class="badge badge-cancelled">Blacklisted</span>
                <span v-else-if="!s.is_active" class="badge badge-closed">Inactive</span>
                <span v-else class="badge badge-open">Active</span>
              </td>
              <td class="text-center">
                <div class="d-flex gap-1 justify-content-center flex-wrap">
                  <button class="btn btn-sm btn-outline-primary" title="Edit" @click="openEdit(s)"><i class="bi bi-pencil"></i></button>
                  <button class="btn btn-sm btn-sm" :class="s.is_active ? 'btn-outline-warning' : 'btn-outline-success'" :title="s.is_active ? 'Deactivate':'Activate'" @click="toggleActive(s)">
                    <i :class="s.is_active ? 'bi bi-toggle-on':'bi bi-toggle-off'"></i>
                  </button>
                  <button class="btn btn-sm" :class="s.is_blacklisted ? 'btn-warning':'btn-outline-danger'" :title="s.is_blacklisted ? 'Remove Blacklist':'Blacklist'" @click="toggleBlacklist(s)">
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
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import EmptyState from '../../components/EmptyState.vue'
import ConfirmationModal from '../../components/ConfirmationModal.vue'
import ToastAlert from '../../components/ToastAlert.vue'
import api from '../../services/api.js'

const toast       = ref(null)
const staff       = ref([])
const loading     = ref(true)
const search      = ref('')
const formModal   = ref(false)
const formLoading = ref(false)
const formError   = ref('')
const editingStaff = ref(null)
const form = ref({ name:'', email:'', phone:'', password:'' })
const modal = ref({ show:false, title:'', message:'', confirmText:'', confirmClass:'btn-danger', loading:false, action:()=>{} })

async function fetchStaff() {
  loading.value = true
  try {
    const res = await api.get('/admin/staff', { params:{ q: search.value } })
    staff.value = res.data.data
  } finally { loading.value = false }
}

function openCreate() {
  editingStaff.value = null
  form.value = { name:'', email:'', phone:'', password:'' }
  formError.value = ''
  formModal.value = true
}
function openEdit(s) {
  editingStaff.value = s
  form.value = { name: s.name, phone: s.phone || '', password:'' }
  formError.value = ''
  formModal.value = true
}

async function submitForm() {
  formError.value = ''
  formLoading.value = true
  try {
    if (editingStaff.value) {
      await api.put(`/admin/staff/${editingStaff.value.id}`, form.value)
      toast.value.show('Staff updated.', 'success')
    } else {
      await api.post('/admin/staff', form.value)
      toast.value.show('Staff created.', 'success')
    }
    formModal.value = false
    fetchStaff()
  } catch (e) {
    formError.value = e.response?.data?.message || 'An error occurred.'
  } finally { formLoading.value = false }
}

async function toggleActive(s) {
  try {
    await api.put(`/admin/staff/${s.id}`, { is_active: !s.is_active })
    toast.value.show(`Staff ${s.is_active ? 'deactivated':'activated'}.`, 'success')
    fetchStaff()
  } catch (e) { toast.value.show(e.response?.data?.message || 'Failed.', 'danger') }
}

async function toggleBlacklist(s) {
  const bl = !s.is_blacklisted
  modal.value = {
    show: true, title: bl ? 'Blacklist Staff':'Remove Blacklist',
    message: bl ? `Blacklist "${s.name}"? Their account will be deactivated.` : `Remove blacklist from "${s.name}"?`,
    confirmText: bl ? 'Blacklist':'Remove',
    confirmClass: bl ? 'btn-danger':'btn-warning',
    loading: false,
    action: async () => {
      modal.value.loading = true
      try {
        await api.put(`/admin/staff/${s.id}`, { is_blacklisted: bl })
        toast.value.show(`Staff ${bl?'blacklisted':'removed from blacklist'}.`, bl?'danger':'success')
        modal.value.show = false
        fetchStaff()
      } catch(e) { modal.value.show = false }
    }
  }
}

onMounted(fetchStaff)
</script>
