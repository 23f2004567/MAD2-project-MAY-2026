/**
 * router/index.js — Vue Router configuration.
 *
 * Route guards redirect users to the correct dashboard based on their role.
 * Frontend guards are UX convenience only; backend enforces real authorization.
 */

import { createRouter, createWebHistory } from 'vue-router'

// Public
import LandingPage  from '../views/LandingPage.vue'

// Auth
import LoginView    from '../views/auth/LoginView.vue'
import RegisterView from '../views/auth/RegisterView.vue'

// Admin
import AdminDashboard from '../views/admin/AdminDashboard.vue'
import AdminTreks     from '../views/admin/AdminTreks.vue'
import AdminStaff     from '../views/admin/AdminStaff.vue'
import AdminUsers     from '../views/admin/AdminUsers.vue'
import AdminBookings  from '../views/admin/AdminBookings.vue'
import AdminReports   from '../views/admin/AdminReports.vue'

// Staff
import StaffDashboard  from '../views/staff/StaffDashboard.vue'
import StaffTreks      from '../views/staff/StaffTreks.vue'
import StaffTrekDetail from '../views/staff/StaffTrekDetail.vue'

// User
import UserDashboard    from '../views/user/UserDashboard.vue'
import BrowseTreks      from '../views/user/BrowseTreks.vue'
import TrekDetail       from '../views/user/TrekDetail.vue'
import MyBookings       from '../views/user/MyBookings.vue'
import TrekkingHistory  from '../views/user/TrekkingHistory.vue'
import UserProfile      from '../views/user/UserProfile.vue'

const routes = [
  { path: '/',         component: LandingPage,  meta: { public: true } },
  { path: '/login',    component: LoginView,    meta: { public: true } },
  { path: '/register', component: RegisterView, meta: { public: true } },

  // Admin routes
  { path: '/admin/dashboard', component: AdminDashboard, meta: { role: 'admin' } },
  { path: '/admin/treks',     component: AdminTreks,     meta: { role: 'admin' } },
  { path: '/admin/staff',     component: AdminStaff,     meta: { role: 'admin' } },
  { path: '/admin/users',     component: AdminUsers,     meta: { role: 'admin' } },
  { path: '/admin/bookings',  component: AdminBookings,  meta: { role: 'admin' } },
  { path: '/admin/reports',   component: AdminReports,   meta: { role: 'admin' } },

  // Staff routes
  { path: '/staff/dashboard',         component: StaffDashboard,  meta: { role: 'staff' } },
  { path: '/staff/treks',             component: StaffTreks,      meta: { role: 'staff' } },
  { path: '/staff/treks/:id',         component: StaffTrekDetail, meta: { role: 'staff' } },

  // User routes
  { path: '/dashboard',  component: UserDashboard,   meta: { role: 'user' } },
  { path: '/treks',      component: BrowseTreks,     meta: { role: 'user' } },
  { path: '/treks/:id',  component: TrekDetail,      meta: { role: 'user' } },
  { path: '/bookings',   component: MyBookings,      meta: { role: 'user' } },
  { path: '/history',    component: TrekkingHistory, meta: { role: 'user' } },
  { path: '/profile',    component: UserProfile,     meta: { role: 'user' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

// Global navigation guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('pp_token')
  const user  = JSON.parse(localStorage.getItem('pp_user') || 'null')

  if (to.meta.public) {
    // Redirect already-logged-in users away from login/register
    if (token && user) return next(_dashboardFor(user.role))
    return next()
  }

  if (!token || !user) return next('/login')

  if (to.meta.role && user.role !== to.meta.role) {
    return next(_dashboardFor(user.role))
  }

  next()
})

function _dashboardFor(role) {
  if (role === 'admin') return '/admin/dashboard'
  if (role === 'staff') return '/staff/dashboard'
  return '/dashboard'
}

export default router
