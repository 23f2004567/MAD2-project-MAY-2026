<template>
  <Sidebar role="admin">
    <ToastAlert ref="toast" />
    <ConfirmationModal
      :visible="modal.show"
      :title="modal.title"
      :message="modal.message"
      :confirm-text="modal.confirmText"
      :confirm-class="modal.confirmClass"
      :loading="modal.loading"
      @confirm="modal.action"
      @cancel="modal.show = false"
    />

    <!-- Trek Form Modal -->
    <Teleport to="body">
      <div v-if="formModal" class="modal fade show d-block" style="background:rgba(0,0,0,0.5);">
        <div class="modal-dialog modal-lg modal-dialog-scrollable modal-dialog-centered">
          <div class="modal-content border-0 rounded-pp shadow">
            <div class="modal-header">
              <h5 class="modal-title fw-bold">
                <i class="bi bi-map me-2 text-pp"></i>{{ editingTrek ? 'Edit Trek' : 'Add New Trek' }}
              </h5>
              <button class="btn-close" @click="closeForm"></button>
            </div>
            <div class="modal-body">
              <div v-if="formError" class="alert alert-danger py-2 small">{{ formError }}</div>
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Trek Name *</label>
                  <input v-model="form.name" type="text" class="form-control" placeholder="e.g. Valley of Flowers" />
                </div>
                <div class="col-md-6">
                  <label class="form-label">Location *</label>
                  <input v-model="form.location" type="text" class="form-control" placeholder="e.g. Uttarakhand, India" />
                </div>
                <div class="col-12">
                  <label class="form-label">Description</label>
                  <textarea v-model="form.description" class="form-control" rows="3" placeholder="Trek description..."></textarea>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Difficulty *</label>
                  <select v-model="form.difficulty" class="form-select">
                    <option>Easy</option>
                    <option>Moderate</option>
                    <option>Hard</option>
                  </select>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Duration (days) *</label>
                  <input v-model.number="form.duration_days" type="number" min="1" class="form-control" />
                </div>
                <div class="col-md-4">
                  <label class="form-label">Total Slots *</label>
                  <input v-model.number="form.total_slots" type="number" min="1" class="form-control" />
                </div>
                <div class="col-md-4">
                  <label class="form-label">Status</label>
                  <select v-model="form.status" class="form-select">
                    <option v-for="s in statuses" :key="s">{{ s }}</option>
                  </select>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Start Date *</label>
                  <input v-model="form.start_date" type="date" class="form-control" />
                </div>
                <div class="col-md-4">
                  <label class="form-label">End Date *</label>
                  <input v-model="form.end_date" type="date" class="form-control" />
                </div>
                <div class="col-md-6">
                  <label class="form-label">Assign Staff</label>
                  <select v-model="form.assigned_staff_id" class="form-select">
                    <option :value="null">— Unassigned —</option>
                    <option v-for="s in staffList" :key="s.id" :value="s.id">{{ s.name }}</option>
                  </select>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn btn-outline-secondary" @click="closeForm">Cancel</button>
              <button class="btn btn-pp px-4" @click="submitForm" :disabled="formLoading">
                <span v-if="formLoading" class="spinner-border spinner-border-sm me-2"></span>
                {{ editingTrek ? 'Save Changes' : 'Create Trek' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Page Header -->
    <div class="pp-page-header">
      <div>
        <h4><i class="bi bi-map me-2 text-pp"></i>Manage Treks</h4>
        <p class="text-muted small mb-0">Create, edit, assign staff and control trek status</p>
      </div>
      <button class="btn btn-pp" @click="openCreate">
        <i class="bi bi-plus-lg me-2"></i>Add Trek
      </button>
    </div>

    <!-- Filters -->
    <div class="pp-card p-3 mb-3">
      <div class="row g-2 align-items-center">
        <div class="col-md-5">
          <div class="input-group search-input-group">
            <span class="input-group-text"><i class="bi bi-search"></i></span>
            <input v-model="search" type="text" class="form-control" placeholder="Search treks..." @input="fetchTreks" />
          </div>
        </div>
        <div class="col-md-3">
          <select v-model="filterStatus" class="form-select" @change="fetchTreks">
            <option value="">All Statuses</option>
            <option v-for="s in statuses" :key="s">{{ s }}</option>
          </select>
        </div>
        <div class="col-md-2">
          <span class="text-muted small">{{ treks.length }} results</span>
        </div>
      </div>
    </div>

    <LoadingSpinner v-if="loading" />

    <div v-else class="pp-card p-0 overflow-hidden">
      <EmptyState v-if="!treks.length" icon="bi bi-map" title="No treks found" message="Add your first trek to get started." />
      <div v-else class="table-responsive">
        <table class="table pp-table mb-0">
          <thead>
            <tr>
              <th>Trek Name</th>
              <th>Location</th>
              <th>Difficulty</th>
              <th>Slots</th>
              <th>Dates</th>
              <th>Status</th>
              <th>Staff</th>
              <th class="text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in treks" :key="t.id">
              <td class="fw-semibold">{{ t.name }}</td>
              <td class="text-muted small"><i class="bi bi-geo-alt me-1"></i>{{ t.location }}</td>
              <td><DifficultyBadge :difficulty="t.difficulty" /></td>
              <td class="small">{{ t.available_slots }}/{{ t.total_slots }}</td>
              <td class="small text-muted">{{ formatDate(t.start_date) }}<br/>{{ formatDate(t.end_date) }}</td>
              <td><StatusBadge :status="t.status" /></td>
              <td class="small text-muted">{{ t.assigned_staff || '—' }}</td>
              <td class="text-center">
                <div class="d-flex gap-1 justify-content-center">
                  <button class="btn btn-sm btn-outline-primary" title="Edit" @click="openEdit(t)"><i class="bi bi-pencil"></i></button>
                  <button class="btn btn-sm btn-outline-danger" title="Delete" @click="confirmDelete(t)"><i class="bi bi-trash"></i></button>
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
import DashboardStatCard from '../../components/DashboardStatCard.vue'
import DifficultyBadge from '../../components/DifficultyBadge.vue'
import StatusBadge from '../../components/StatusBadge.vue'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import EmptyState from '../../components/EmptyState.vue'
import ConfirmationModal from '../../components/ConfirmationModal.vue'
import ToastAlert from '../../components/ToastAlert.vue'
import api from '../../services/api.js'

const toast       = ref(null)
const treks       = ref([])
const staffList   = ref([])
const loading     = ref(true)
const search      = ref('')
const filterStatus = ref('')
const formModal   = ref(false)
const formLoading = ref(false)
const formError   = ref('')
const editingTrek = ref(null)
const statuses    = ['Pending','Approved','Open','Closed','Completed']

const form = ref(blankForm())
function blankForm() {
  return { name:'', location:'', description:'', difficulty:'Easy', duration_days:5, total_slots:20, status:'Pending', start_date:'', end_date:'', assigned_staff_id:null }
}

const modal = ref({ show:false, title:'', message:'', confirmText:'', confirmClass:'btn-danger', loading:false, action:()=>{} })

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' })
}

async function fetchTreks() {
  loading.value = true
  try {
    const res = await api.get('/admin/treks', { params: { q: search.value, status: filterStatus.value } })
    treks.value = res.data.data
  } finally { loading.value = false }
}

async function fetchStaff() {
  const res = await api.get('/admin/staff')
  staffList.value = res.data.data
}

function openCreate() {
  editingTrek.value = null
  form.value = blankForm()
  formError.value = ''
  formModal.value = true
}
function openEdit(t) {
  editingTrek.value = t
  form.value = {
    name: t.name, location: t.location, description: t.description || '',
    difficulty: t.difficulty, duration_days: t.duration_days, total_slots: t.total_slots,
    status: t.status, start_date: t.start_date, end_date: t.end_date,
    assigned_staff_id: t.assigned_staff_id,
  }
  formError.value = ''
  formModal.value = true
}
function closeForm() { formModal.value = false }

async function submitForm() {
  formError.value = ''
  formLoading.value = true
  try {
    if (editingTrek.value) {
      await api.put(`/admin/treks/${editingTrek.value.id}`, form.value)
      toast.value.show('Trek updated successfully.', 'success')
    } else {
      await api.post('/admin/treks', form.value)
      toast.value.show('Trek created successfully.', 'success')
    }
    closeForm()
    fetchTreks()
  } catch (e) {
    formError.value = e.response?.data?.message || 'An error occurred.'
  } finally {
    formLoading.value = false
  }
}

function confirmDelete(t) {
  modal.value = {
    show: true,
    title: 'Delete Trek',
    message: `Are you sure you want to delete "${t.name}"? This cannot be undone.`,
    confirmText: 'Delete',
    confirmClass: 'btn-danger',
    loading: false,
    action: async () => {
      modal.value.loading = true
      try {
        await api.delete(`/admin/treks/${t.id}`)
        toast.value.show('Trek deleted.', 'success')
        modal.value.show = false
        fetchTreks()
      } catch (e) {
        toast.value.show(e.response?.data?.message || 'Delete failed.', 'danger')
        modal.value.show = false
      }
    }
  }
}

onMounted(() => { fetchTreks(); fetchStaff() })
</script>
