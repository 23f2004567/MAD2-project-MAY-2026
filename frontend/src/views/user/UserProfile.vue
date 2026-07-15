<template>
  <div>
    <Navbar />
    <div class="container py-4" style="max-width:640px; margin:auto;">
      <ToastAlert ref="toast" />

      <div class="pp-page-header">
        <h4><i class="bi bi-person-circle me-2 text-pp"></i>My Profile</h4>
      </div>

      <div class="pp-card p-4">
        <div v-if="!editing">
          <div class="text-center mb-4">
            <div class="rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width:80px;height:80px;background:var(--pp-green-pale);font-size:2rem;color:var(--pp-green);">
              {{ initials }}
            </div>
            <h5 class="fw-bold mb-0">{{ user.name }}</h5>
            <p class="text-muted small">{{ user.email }}</p>
            <span class="badge badge-open text-capitalize">{{ user.role }}</span>
          </div>
          <table class="table table-borderless table-sm">
            <tbody>
              <tr><td class="text-muted fw-semibold small" style="width:130px;">Phone</td><td class="small">{{ user.phone || '—' }}</td></tr>
              <tr><td class="text-muted fw-semibold small">Member Since</td><td class="small">{{ formatDate(user.created_at) }}</td></tr>
              <tr><td class="text-muted fw-semibold small">Account Status</td>
                <td><span class="badge" :class="user.is_active ? 'badge-open':'badge-closed'">{{ user.is_active ? 'Active':'Inactive' }}</span></td>
              </tr>
            </tbody>
          </table>
          <button class="btn btn-pp w-100 mt-2" @click="startEdit">
            <i class="bi bi-pencil me-2"></i>Edit Profile
          </button>
        </div>

        <!-- Edit form -->
        <div v-else>
          <h6 class="fw-bold mb-4">Edit Profile</h6>
          <div v-if="formError" class="alert alert-danger py-2 small">{{ formError }}</div>
          <div class="mb-3">
            <label class="form-label">Full Name</label>
            <input v-model="form.name" type="text" class="form-control" />
          </div>
          <div class="mb-3">
            <label class="form-label">Phone Number</label>
            <input v-model="form.phone" type="tel" class="form-control" />
          </div>
          <hr />
          <p class="small text-muted">Change Password <span class="fw-normal">(leave blank to keep current)</span></p>
          <div class="mb-3">
            <label class="form-label">New Password</label>
            <input v-model="form.password" type="password" class="form-control" placeholder="Min. 6 characters" />
          </div>
          <div class="mb-4">
            <label class="form-label">Confirm Password</label>
            <input v-model="form.confirm_password" type="password" class="form-control" />
            <div v-if="pwMismatch" class="small text-danger mt-1"><i class="bi bi-x-circle me-1"></i>Passwords do not match</div>
          </div>
          <div class="d-flex gap-2">
            <button class="btn btn-outline-secondary flex-grow-1" @click="editing=false">Cancel</button>
            <button class="btn btn-pp flex-grow-1" @click="saveProfile" :disabled="saving || pwMismatch">
              <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Navbar from '../../components/Navbar.vue'
import ToastAlert from '../../components/ToastAlert.vue'
import api from '../../services/api.js'

const toast   = ref(null)
const user    = ref({})
const editing = ref(false)
const saving  = ref(false)
const formError = ref('')
const form    = ref({ name:'', phone:'', password:'', confirm_password:'' })

const initials   = computed(() => (user.value.name || 'U').split(' ').map(n=>n[0]).slice(0,2).join('').toUpperCase())
const pwMismatch = computed(() => form.value.confirm_password && form.value.password !== form.value.confirm_password)

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN', { day:'2-digit', month:'long', year:'numeric' })
}

async function fetchProfile() {
  const res = await api.get('/user/profile')
  user.value = res.data.data
  localStorage.setItem('pp_user', JSON.stringify(res.data.data))
}

function startEdit() {
  form.value = { name: user.value.name, phone: user.value.phone || '', password:'', confirm_password:'' }
  formError.value = ''
  editing.value = true
}

async function saveProfile() {
  if (pwMismatch.value) return
  formError.value = ''
  saving.value = true
  try {
    const payload = { name: form.value.name, phone: form.value.phone }
    if (form.value.password) { payload.password = form.value.password; payload.confirm_password = form.value.confirm_password }
    await api.put('/user/profile', payload)
    toast.value.show('Profile updated successfully.', 'success')
    editing.value = false
    fetchProfile()
  } catch(e) {
    formError.value = e.response?.data?.message || 'Update failed.'
  } finally { saving.value = false }
}

onMounted(fetchProfile)
</script>
