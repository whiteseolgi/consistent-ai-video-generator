<script lang="ts">
  import { isLoading, loadingMessage } from '$lib/stores';
</script>

{#if $isLoading}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-8 max-w-sm w-full">
      <div class="flex flex-col items-center">
        <!-- Spinner -->
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
        
        <!-- Loading Message -->
        <p class="text-gray-700 text-center">
          {$loadingMessage || '처리 중...'}
        </p>
      </div>
    </div>
  </div>
{/if}