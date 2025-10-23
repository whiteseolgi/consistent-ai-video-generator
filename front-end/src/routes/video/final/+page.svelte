<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import { projectState } from '$lib/stores';
  let videoUrl = '';
  let isLoading = false;  // Start with false, set to true only when actually loading
  let hasVideo = false;
  
  // Load existing final video on mount - use dedicated endpoint
  onMount(async () => {
    if ($projectState.work_dir && $projectState.entity_set_name) {
      try {
        // Use API client method to get correct URL (async version)
        videoUrl = await api.getFinalVideoUrlAsync($projectState.work_dir, $projectState.entity_set_name);
        console.log('Video URL:', videoUrl);
        console.log('Project state:', {
          work_dir: $projectState.work_dir,
          entity_set_name: $projectState.entity_set_name
        });
        
        // Test if video exists using HEAD request
        const response = await fetch(videoUrl, { method: 'HEAD' });
        console.log('HEAD response status:', response.status);
        if (response.ok) {
          hasVideo = true;
        } else {
          console.error('Video not found, status:', response.status);
          hasVideo = false;
        }
      } catch (error) {
        console.error('Error checking video:', error);
        // Fallback to synchronous method
        videoUrl = api.getFinalVideoUrl($projectState.work_dir, $projectState.entity_set_name);
        // Still try to show video element, let it handle the error
        hasVideo = true;
      }
    }
  });
  
  function handleVideoError(event) {
    console.error('Video load error:', event);
    console.error('Failed URL:', videoUrl);
    console.error('Video element error:', event.target.error);
    hasVideo = false;
  }
  
  function handleVideoLoad() {
    console.log('Video loaded successfully');
    console.log('Video src:', event.target.src);
    hasVideo = true;
  }
</script>

<div class="max-w-5xl mx-auto">
  <h1 class="text-3xl font-bold mb-8 text-white">최종 영상</h1>
  
  {#if isLoading}
    <div class="card bg-base-100 shadow">
      <div class="card-body items-center text-center">
        <p class="opacity-70">로딩 중...</p>
      </div>
    </div>
  {:else if !hasVideo}
    <div class="card bg-base-100 shadow">
      <div class="card-body items-center text-center">
        <p class="opacity-70 mb-4">아직 생성된 영상이 없습니다.</p>
        <button onclick={() => goto('/video/images')} class="btn btn-primary">영상 생성으로 이동</button>
      </div>
    </div>
  {:else}
    <div class="card bg-base-100 shadow">
      <div class="card-body">
      <video
        src={videoUrl}
        controls
        class="w-full rounded-lg"
        onerror={handleVideoError}
        onloadeddata={handleVideoLoad}
      ><track kind="captions" srclang="ko" label="Korean" /></video>
      
      <div class="mt-6 flex justify-between">
        <div class="text-sm opacity-70">
          <p>최종 영상</p>
        </div>
        
        <a
          href={videoUrl}
          download
          class="btn btn-success"
        >
          다운로드
        </a>
      </div>
      </div>
    </div>
    
    <!-- Action Buttons -->
    <div class="flex justify-end mt-8 gap-3">
      <button onclick={() => goto('/')} class="btn btn-ghost">새 프로젝트</button>
      <button onclick={() => goto('/video/images')} class="btn btn-primary">다시 생성</button>
    </div>
  {/if}
</div>