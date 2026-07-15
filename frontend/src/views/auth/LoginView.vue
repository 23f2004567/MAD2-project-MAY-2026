<template>
  <div class="auth-page">
    <!-- Hero text -->
    <div class="text-center mb-4">
      <div class="auth-hero-title">Peak<span>Path</span></div>
      <p class="pp-tagline" style="color:rgba(255,255,255,0.7);">Explore. Book. Trek.</p>
    </div>

    <div class="auth-card">
      <h4 class="fw-bold mb-1 text-center">Welcome back</h4>
      <p class="text-muted text-center small mb-4">Sign in to your account</p>

      <div v-if="error" class="alert alert-danger py-2 small">
        <i class="bi bi-exclamation-circle me-2"></i>{{ error }}
      </div>

      <form @submit.prevent="login">
        <div class="mb-3">
          <label class="form-label" for="login-email">Email address</label>
          <div class="input-group">
            <span class="input-group-text bg-light"><i class="bi bi-envelope text-muted"></i></span>
            <input
              id="login-email"
              v-model="form.email"
              type="email"
              class="form-control"
              placeholder="you@example.com"
              required
              autocomplete="email"
            />
          </div>
        </div>

        <div class="mb-4">
          <label class="form-label" for="login-password">Password</label>
          <div class="input-group">
            <span class="input-group-text bg-light"><i class="bi bi-lock text-muted"></i></span>
            <input
              id="login-password"
              v-model="form.password"
              :type="showPw ? 'text' : 'password'"
              class="form-control"
              placeholder="••••••••"
              required
            />
            <button type="button" class="input-group-text bg-light border" @click="showPw = !showPw" tabindex="-1">
              <i :class="showPw ? 'bi bi-eye-slash' : 'bi bi-eye'" class="text-muted"></i>
            </button>
          </div>
        </div>

        <button type="submit" class="btn btn-pp w-100 py-2 mb-3" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          Sign In
        </button>

        <p class="text-center small mb-0 text-muted">
          New to PeakPath?
          <router-link to="/register" class="text-pp fw-semibold">Create an account</router-link>
        </p>
      </form>

      <hr class="my-4" />
      <div class="text-center">
        <p class="small text-muted mb-1 fw-semibold">Demo Credentials</p>
        <div class="d-flex gap-2 justify-content-center flex-wrap">
          <button class="btn btn-outline-secondary btn-sm" @click="fillDemo('admin@peakpath.com','Admin@123')">
            <i class="bi bi-shield me-1"></i>Admin
          </button>
          <button class="btn btn-outline-secondary btn-sm" @click="fillDemo('rajan@peakpath.com','Staff@123')">
            <i class="bi bi-person-badge me-1"></i>Staff
          </button>
          <button class="btn btn-outline-secondary btn-sm" @click="fillDemo('arjun@example.com','User@123')">
            <i class="bi bi-person me-1"></i>User
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api.js'

const router = useRouter()
const form   = ref({ email: '', password: '' })
const error  = ref('')
const loading = ref(false)
const showPw  = ref(false)

function fillDemo(email, pw) {
  form.value.email    = email
  form.value.password = pw
}

async function login() {
  error.value   = ''
  loading.value = true
  try {
    const res = await api.post('/auth/login', form.value)
    localStorage.setItem('pp_token', res.data.token)
    localStorage.setItem('pp_user', JSON.stringify(res.data.user))
    const role = res.data.user.role
    if (role === 'admin') router.push('/admin/dashboard')
    else if (role === 'staff') router.push('/staff/dashboard')
    else router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.message || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
