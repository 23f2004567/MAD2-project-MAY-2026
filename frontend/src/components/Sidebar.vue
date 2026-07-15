<template>
  <!-- Admin/Staff sidebar layout shell -->
  <div>
    <!-- Mobile overlay -->
    <div class="sidebar-overlay" :class="{ show: open }" @click="open = false"></div>

    <!-- Sidebar -->
    <aside class="pp-sidebar" :class="{ open }">
      <div class="sidebar-brand">
        <div class="pp-brand">Peak<span>Path</span></div>
        <div class="pp-tagline">Explore. Book. Trek.</div>
      </div>

      <nav>
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-link"
          active-class="active"
          @click="open = false"
        >
          <i :class="item.icon"></i>
          {{ item.label }}
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="fw-semibold text-white-50 mb-1 small">{{ user?.name }}</div>
        <div class="text-capitalize" style="color:rgba(255,255,255,0.3);font-size:0.75rem;">{{ user?.role }}</div>
        <button class="btn btn-sm mt-2 w-100" style="background:rgba(255,255,255,0.1);color:#fff;border:none;border-radius:8px;" @click="logout">
          <i class="bi bi-box-arrow-right me-1"></i> Logout
        </button>
      </div>
    </aside>

    <!-- Main content -->
    <div class="pp-main">
      <!-- Topbar -->
      <div class="pp-topbar">
        <button class="btn d-lg-none p-1" @click="open = !open" style="border:none;">
          <i class="bi bi-list fs-4 text-pp"></i>
        </button>
        <div class="ms-auto d-flex align-items-center gap-3">
          <span class="badge bg-pp px-3 py-2 text-capitalize">{{ user?.role }}</span>
          <span class="fw-semibold small d-none d-md-inline">{{ user?.name }}</span>
        </div>
      </div>

      <div class="pp-content">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api.js'

const props = defineProps({ role: { type: String, required: true } })
const router = useRouter()
const open   = ref(false)
const user   = computed(() => JSON.parse(localStorage.getItem('pp_user') || 'null'))

const adminNav = [
  { to: '/admin/dashboard', icon: 'bi bi-speedometer2', label: 'Dashboard' },
  { to: '/admin/treks',     icon: 'bi bi-map',          label: 'Treks' },
  { to: '/admin/staff',     icon: 'bi bi-person-badge', label: 'Staff' },
  { to: '/admin/users',     icon: 'bi bi-people',       label: 'Users' },
  { to: '/admin/bookings',  icon: 'bi bi-journal-check',label: 'Bookings' },
  { to: '/admin/reports',   icon: 'bi bi-bar-chart-line',label: 'Reports' },
]
const staffNav = [
  { to: '/staff/dashboard', icon: 'bi bi-speedometer2', label: 'Dashboard' },
  { to: '/staff/treks',     icon: 'bi bi-map',          label: 'My Treks' },
]
const navItems = computed(() => props.role === 'admin' ? adminNav : staffNav)

async function logout() {
  try { await api.post('/auth/logout') } catch {}
  localStorage.removeItem('pp_token')
  localStorage.removeItem('pp_user')
  router.push('/login')
}
</script>
