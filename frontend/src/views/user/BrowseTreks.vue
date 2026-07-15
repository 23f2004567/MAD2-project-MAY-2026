<template>
  <div>
    <Navbar />
    <div class="container-fluid py-4 px-3 px-md-4" style="max-width:1200px; margin:auto;">

      <!-- Header & filters -->
      <div class="pp-page-header">
        <div>
          <h4><i class="bi bi-map me-2 text-pp"></i>Browse Treks</h4>
          <p class="text-muted small mb-0">Discover and book your next adventure</p>
        </div>
      </div>

      <!-- Search & Filters -->
      <div class="pp-card p-3 mb-4">
        <div class="row g-2">
          <div class="col-md-4">
            <div class="input-group search-input-group">
              <span class="input-group-text"><i class="bi bi-search"></i></span>
              <input v-model="filters.q" type="text" class="form-control" placeholder="Search trek name..." @input="fetchTreks" />
            </div>
          </div>
          <div class="col-md-3">
            <input v-model="filters.location" type="text" class="form-control" placeholder="Location..." @input="fetchTreks" />
          </div>
          <div class="col-md-2">
            <select v-model="filters.difficulty" class="form-select" @change="fetchTreks">
              <option value="">All Difficulties</option>
              <option>Easy</option><option>Moderate</option><option>Hard</option>
            </select>
          </div>
          <div class="col-md-2">
            <select v-model="filters.duration" class="form-select" @change="fetchTreks">
              <option value="">Any Duration</option>
              <option value="3">Up to 3 days</option>
              <option value="7">Up to 7 days</option>
              <option value="14">Up to 14 days</option>
            </select>
          </div>
          <div class="col-md-1">
            <button class="btn btn-outline-secondary w-100" @click="clearFilters" title="Clear filters">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>
        </div>
      </div>

      <LoadingSpinner v-if="loading" />

      <template v-else>
        <p class="text-muted small mb-3">{{ treks.length }} trek(s) found</p>
        <EmptyState v-if="!treks.length" icon="bi bi-map" title="No treks found" message="Try adjusting your search filters." />
        <div v-else class="row g-3">
          <div v-for="t in treks" :key="t.id" class="col-md-6 col-lg-4">
            <TrekCard :trek="t" />
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '../../components/Navbar.vue'
import TrekCard from '../../components/TrekCard.vue'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import EmptyState from '../../components/EmptyState.vue'
import api from '../../services/api.js'

const treks   = ref([])
const loading = ref(true)
const filters = ref({ q:'', location:'', difficulty:'', duration:'' })

async function fetchTreks() {
  loading.value = true
  try {
    const res = await api.get('/treks', { params: filters.value })
    treks.value = res.data.data
  } finally { loading.value = false }
}

function clearFilters() {
  filters.value = { q:'', location:'', difficulty:'', duration:'' }
  fetchTreks()
}

onMounted(fetchTreks)
</script>
