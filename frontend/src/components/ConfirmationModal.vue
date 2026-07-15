<template>
  <!-- Confirmation modal — used for delete/cancel/blacklist actions -->
  <Teleport to="body">
    <div v-if="visible" class="modal fade show d-block" tabindex="-1" style="background:rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content rounded-pp border-0 shadow">
          <div class="modal-header border-bottom">
            <h5 class="modal-title">
              <i :class="icon" class="me-2"></i>{{ title }}
            </h5>
            <button type="button" class="btn-close" @click="$emit('cancel')"></button>
          </div>
          <div class="modal-body py-4">
            <p class="mb-0 text-muted">{{ message }}</p>
          </div>
          <div class="modal-footer border-top gap-2">
            <button class="btn btn-outline-secondary btn-sm px-4" @click="$emit('cancel')">Cancel</button>
            <button class="btn btn-sm px-4" :class="confirmClass" @click="$emit('confirm')" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              {{ confirmText }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  visible:      { type: Boolean, default: false },
  title:        { type: String, default: 'Confirm Action' },
  message:      { type: String, default: 'Are you sure?' },
  confirmText:  { type: String, default: 'Confirm' },
  confirmClass: { type: String, default: 'btn-danger' },
  icon:         { type: String, default: 'bi bi-exclamation-triangle text-warning' },
  loading:      { type: Boolean, default: false },
})
defineEmits(['confirm', 'cancel'])
</script>
