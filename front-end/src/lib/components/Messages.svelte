<script lang="ts">
  import { errorMessage, successMessage } from '$lib/stores';
</script>

<!-- Success Message -->
{#if $successMessage}
  <div class="fixed top-4 right-4 bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg shadow-lg z-50 flex items-center space-x-2">
    <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
    </svg>
    <span>{$successMessage}</span>
  </div>
{/if}

<!-- Error Message -->
{#if $errorMessage}
  <div class="fixed top-4 right-4 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg shadow-lg z-50 flex items-center space-x-2">
    <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
    </svg>
    <span>{$errorMessage}</span>
  </div>
{/if}