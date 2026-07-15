<template>
  <div class="auth-page">
    <div class="text-center mb-4">
      <div class="auth-hero-title">Peak<span>Path</span></div>
      <p class="pp-tagline" style="color:rgba(255,255,255,0.7);">Explore. Book. Trek.</p>
    </div>

    <div class="auth-card" style="max-width:480px;">
      <h4 class="fw-bold mb-1 text-center">Create Account</h4>
      <p class="text-muted text-center small mb-4">Join PeakPath and start your adventure</p>

      <div v-if="error" class="alert alert-danger py-2 small">
        <i class="bi bi-exclamation-circle me-2"></i>{{ error }}
      </div>

      <form @submit.prevent="register">
        <div class="mb-3">
          <label class="form-label" for="reg-name">Full Name</label>
          <div class="input-group">
            <span class="input-group-text bg-light"><i class="bi bi-person text-muted"></i></span>
            <input id="reg-name" v-model="form.name" type="text" class="form-control" placeholder="Your full name" required />
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label" for="reg-email">Email Address</label>
          <div class="input-group">
            <span class="input-group-text bg-light"><i class="bi bi-envelope text-muted"></i></span>
            <input id="reg-email" v-model="form.email" type="email" class="form-control" placeholder="you@example.com" required />
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label" for="reg-phone">Phone Number <span class="text-muted fw-normal">(optional)</span></label>
          <div class="input-group">
            <span class="input-group-text bg-light"><i class="bi bi-telephone text-muted"></i></span>
            <input id="reg-phone" v-model="form.phone" type="tel" class="form-control" placeholder="+91 9XXXXXXXXX" />
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label" for="reg-password">Password</label>
          <div class="input-group">
            <span class="input-group-text bg-light"><i class="bi bi-lock text-muted"></i></span>
            <input id="reg-password" v-model="form.password" :type="showPw?'text':'password'" class="form-control" placeholder="Min. 6 characters" required />
            <button type="button" class="input-group-text bg-light border" @click="showPw = !showPw" tabindex="-1">
              <i :class="showPw ? 'bi bi-eye-slash':'bi bi-eye'" class="text-muted"></i>
            </button>
          </div>
        </div>

        <div class="mb-4">
          <label class="form-label" for="reg-confirm">Confirm Password</label>
          <div class="input-group">
            <span class="input-group-text bg-light"><i class="bi bi-lock-fill text-muted"></i></span>
            <input id="reg-confirm" v-model="form.confirm_password" :type="showPw?'text':'password'" class="form-control" placeholder="Repeat password" required />
          </div>
          <div v-if="pwMismatch" class="small text-danger mt-1"><i class="bi bi-x-circle me-1"></i>Passwords do not match</div>
        </div>

        <button type="submit" class="btn btn-pp w-100 py-2 mb-3" :disabled="loading || pwMismatch">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          Create Account
        </button>

        <p class="text-center small mb-0 text-muted">
          Already have an account?
          <router-link to="/login" class="text-pp fw-semibold">Sign in</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api.js'

const router  = useRouter()
const form    = ref({ name: '', email: '', phone: '', password: '', confirm_password: '' })
const error   = ref('')
const loading = ref(false)
const showPw  = ref(false)
const pwMismatch = computed(() => form.value.confirm_password && form.value.password !== form.value.confirm_password)

async function register() {
  if (pwMismatch.value) return
  error.value   = ''
  loading.value = true
  try {
    const res = await api.post('/auth/register', form.value)
    localStorage.setItem('pp_token', res.data.token)
    localStorage.setItem('pp_user', JSON.stringify(res.data.user))
    router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.message || 'Registration failed.'
  } finally {
    loading.value = false
  }
}
</script>
