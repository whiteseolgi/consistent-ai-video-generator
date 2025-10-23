<script lang="ts">
  import type { EntityTuple } from '$lib/types';
  import { projectState } from '$lib/stores';
  import { api } from '$lib/api';
  
  export let entity: EntityTuple;
  export let index: number;
  export let onclick: () => void = () => {};
  
  $: [type, name, description, imagePath] = entity;
  $: typeLabel = type === 'character' ? '인물' : type === 'location' ? '배경' : '사물';
  $: typeColor = type === 'character' ? 'bg-blue-100' : type === 'location' ? 'bg-green-100' : 'bg-purple-100';
  
  let imageUrl: string | null = null;
  
  // Convert file path to URL for display
  async function updateImageUrl(path: string | null) {
    if (!path || path === 'None' || path === 'null') {
      imageUrl = null;
      return;
    }
    // If it's already a URL, return as-is
    if (path.startsWith('http://') || path.startsWith('https://')) {
      imageUrl = path;
      return;
    }
    // For local files, use API client method to get correct URL
    try {
      imageUrl = await api.getImageUrlAsync($projectState.work_dir, $projectState.entity_set_name, path);
      console.log('Entity image URL updated:', imageUrl);
    } catch (error) {
      console.error('Failed to generate image URL:', error);
      // Fallback to synchronous method
      imageUrl = api.getImageUrl($projectState.work_dir, $projectState.entity_set_name, path);
    }
  }
  
  // Update image URL when imagePath changes
  $: updateImageUrl(imagePath);
</script>

<button {onclick} class="card bg-base-100 shadow hover:shadow-lg transition-shadow flex-shrink-0" style="width: 300px; border: 1px solid #0f0f0f; margin: 2px;">
  <!-- Image -->
  <div class="h-40 bg-base-200 relative">
    {#if imageUrl}
      <img
        src={imageUrl}
        alt={name}
        class="w-full h-full object-cover"
      />
    {:else}
      <div class="w-full h-full flex items-center justify-center opacity-60">
        <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
    {/if}
    
    <!-- Type Badge -->
    <div class="absolute top-2 left-2 badge badge-outline badge-sm">
      {typeLabel}
    </div>
  </div>
  
  <!-- Content -->
  <div class="card-body p-3">
    <h3 class="card-title text-sm mb-1">{name}</h3>
    <p class="text-xs line-clamp-2">{description}</p>
  </div>
</button>