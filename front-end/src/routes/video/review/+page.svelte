<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import { projectState, cuts, getCutId, setLoading, showSuccess, showError } from '$lib/stores';
  
  let videoClips: Array<{
    scene_num: number;
    cut_num: number;
    filename: string;
    url: string;
  }> = [];
  
  // Load existing cut videos and cuts on mount
  onMount(async () => {
    if ($projectState.work_dir && $projectState.entity_set_name) {
      // Load cuts first if not already loaded
      const loadedCuts = await api.loadCuts($projectState.work_dir, $projectState.entity_set_name);
      if (loadedCuts && loadedCuts.length > 0) {
        cuts.set(loadedCuts);
      }
      
      // Then load videos
      const videos = await api.loadCutVideos($projectState.work_dir, $projectState.entity_set_name);
      if (videos && videos.length > 0) {
        // Use Promise.all to generate all URLs asynchronously
        const videoPromises = videos.map(async (video) => {
          try {
            const url = await api.getVideoUrlAsync($projectState.work_dir, $projectState.entity_set_name, video.path);
            return { ...video, url };
          } catch (error) {
            console.error('Failed to generate video URL for', video.filename, error);
            // Fallback to synchronous method
            const url = api.getVideoUrl($projectState.work_dir, $projectState.entity_set_name, video.path);
            return { ...video, url };
          }
        });
        
        videoClips = await Promise.all(videoPromises);
        console.log('Video clips loaded:', videoClips.length);
      }
    }
  });
  
  async function concatenateVideos() {
    setLoading(true, '영상 합치는 중...');
    
    try {
      const result = await api.concatVideos({
        entity_set_name: $projectState.entity_set_name,
        work_dir: $projectState.work_dir
      });
      
      showSuccess('최종 영상 생성 완료');
      goto('/video/final');
    } catch (error) {
      showError('영상 병합 중 오류가 발생했습니다');
      console.error(error);
    } finally {
      setLoading(false);
    }
  }
</script>

<div class="max-w-6xl mx-auto">
  <h1 class="text-3xl font-bold mb-8 text-white">컷 영상 스토리보드 확인</h1>
  
  <div class="card bg-base-100 shadow">
    <div class="card-body">
    <p class="opacity-70 mb-6">생성된 영상 클립들을 확인하고 최종 영상으로 합칩니다.</p>
    
    <!-- Video Grid -->
    <div class="grid grid-cols-4 gap-4 mb-8">
      {#each videoClips as clip}
        <div class="card bg-base-100 shadow overflow-hidden">
          <video src={clip.url} controls class="w-full aspect-video"><track kind="captions" srclang="ko" label="Korean" /></video>
          <div class="p-3">
            <p class="text-sm font-semibold">S{String(clip.scene_num).padStart(2, '0')}-C{String(clip.cut_num).padStart(2, '0')}</p>
            <p class="text-xs opacity-70">{clip.filename}</p>
          </div>
        </div>
      {/each}
      
      {#if videoClips.length === 0}
        <div class="col-span-full text-center py-12 opacity-60">생성된 영상 클립이 여기에 표시됩니다</div>
      {/if}
    </div>
    
    <!-- Action Button -->
    <div class="card-actions justify-end">
      <button onclick={concatenateVideos} class="btn btn-primary">영상 합치기</button>
    </div>
    </div>
  </div>
</div>