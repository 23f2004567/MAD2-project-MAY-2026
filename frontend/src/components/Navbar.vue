<template>
  <!-- User-facing top navbar -->
  <nav class="navbar navbar-expand-lg" style="background:var(--pp-green-dark); padding: 0 1.5rem;">
    <router-link class="navbar-brand pp-brand" to="/dashboard" style="color:#fff;">
      Peak<span>Path</span>
    </router-link>

    <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#userNav">
      <i class="bi bi-list text-white fs-4"></i>
    </button>

    <div class="collapse navbar-collapse" id="userNav">
      <ul class="navbar-nav me-auto gap-1 py-2 py-lg-0">
        <li class="nav-item">
          <router-link class="nav-link text-white-75 px-3" active-class="active-nav" to="/dashboard">
            <i class="bi bi-speedometer2 me-1"></i>Dashboard
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link text-white-75 px-3" active-class="active-nav" to="/treks">
            <i class="bi bi-map me-1"></i>Browse Treks
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link text-white-75 px-3" active-class="active-nav" to="/bookings">
            <i class="bi bi-journal-check me-1"></i>My Bookings
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link text-white-75 px-3" active-class="active-nav" to="/history">
            <i class="bi bi-clock-history me-1"></i>History
          </router-link>
        </li>
      </ul>
      <div class="d-flex align-items-center gap-3">
        <router-link to="/profile" class="text-white-50 small text-decoration-none d-flex align-items-center gap-2">
          <i class="bi bi-person-circle fs-5 text-white"></i>
          <span class="d-none d-lg-inline">{{ user?.name }}</span>
        </router-link>
        <button class="btn btn-sm btn-pp-outline" style="border-color:rgba(255,255,255,0.3);color:#fff;" @click="logout">
          <i class="bi bi-box-arrow-right me-1"></i>Logout
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api.js'

const router = useRouter()
const user   = computed(() => JSON.parse(localStorage.getItem('pp_user') || 'null'))

async function logout() {
  try { await api.post('/auth/logout') } catch {}
  localStorage.removeItem('pp_token')
  localStorage.removeItem('pp_user')
  router.push('/login')
}
</script>

<style scoped>
.text-white-75 { color: rgba(255,255,255,0.75) !important; }
.active-nav { color: #fff !important; font-weight: 600; }
</style>
