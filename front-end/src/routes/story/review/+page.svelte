<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import { scenes, cuts, entityList, projectState } from '$lib/stores';
  import CutCard from '$lib/components/CutCard.svelte';
  import EntityCard from '$lib/components/EntityCard.svelte';
  import type { Cut } from '$lib/types';
  
  let expandedCut: string | null = null;
  
  // Load existing data on mount
  onMount(async () => {
    if ($projectState.work_dir && $projectState.entity_set_name) {
      // Load entities if not already loaded
      if ($entityList.length === 0) {
        const entities = await api.loadEntityList($projectState.work_dir, $projectState.entity_set_name);
        if (entities && entities.length > 0) {
          entityList.set(entities);
        }
      }
      
      // Load scenes
      if ($scenes.length === 0) {
        const loadedScenes = await api.loadScenes($projectState.work_dir, $projectState.entity_set_name);
        if (loadedScenes && loadedScenes.length > 0) {
          scenes.set(loadedScenes);
        }
      }
      
      // Load cuts
      if ($cuts.length === 0) {
        const loadedCuts = await api.loadCuts($projectState.work_dir, $projectState.entity_set_name);
        if (loadedCuts && loadedCuts.length > 0) {
          cuts.set(loadedCuts);
        }
      }
    }
  });
  
  function toggleCut(sceneNum: number, cutNum: number) {
    const cutId = `${sceneNum}-${cutNum}`;
    expandedCut = expandedCut === cutId ? null : cutId;
  }
  
  function getMatchedEntities(cut: Cut) {
    if (!cut.entities) return [];
    return $entityList.filter(e => cut.entities?.includes(e[1]));
  }
</script>

<div class="max-w-5xl mx-auto">
  <h1 class="text-3xl font-bold mb-8 text-white">씬/컷 확인</h1>
  
  {#if $cuts.length === 0}
    <div class="card bg-base-100 shadow">
      <div class="card-body items-center text-center">
        <p class="opacity-70 mb-4">아직 분석된 씬/컷이 없습니다.</p>
        <button onclick={() => goto('/story/input')} class="btn btn-primary">스토리 입력으로 이동</button>
      </div>
    </div>
  {:else}
    <div class="space-y-8">
      {#each $cuts as sceneCuts, sceneIndex}
        <div class="card bg-base-100 shadow">
          <div class="card-body">
          <h2 class="text-xl font-semibold mb-4">
            씬 {sceneIndex + 1}
            {#if $scenes[sceneIndex]}
              <span class="text-sm font-normal opacity-70 ml-2">
                {$scenes[sceneIndex].description}
              </span>
            {/if}
          </h2>
          
          <div class="space-y-3">
            {#each sceneCuts as cut, cutIndex}
              {@const isExpanded = expandedCut === `${sceneIndex + 1}-${cutIndex + 1}`}
              <div>
                <CutCard
                  sceneNum={sceneIndex + 1}
                  cutNum={cutIndex + 1}
                  {cut}
                  expanded={isExpanded}
                  onclick={() => toggleCut(sceneIndex + 1, cutIndex + 1)}
                />
                
                {#if isExpanded}
                  {@const matchedEntities = getMatchedEntities(cut)}
                  {#if matchedEntities.length > 0}
                    <div class="mt-3 p-4 bg-base-200 rounded-lg">
                      <h3 class="text-sm font-semibold mb-3">매칭된 레퍼런스</h3>
                      <div class="flex gap-3 overflow-x-auto">
                        {#each matchedEntities as entity, idx}
                          <div class="flex-shrink-0">
                            <EntityCard {entity} index={idx} />
                          </div>
                        {/each}
                      </div>
                    </div>
                  {/if}
                  
                  <!-- Additional cut details -->
                  <div class="mt-3 p-4 bg-base-200 rounded-lg">
                    <h3 class="text-sm font-semibold mb-2">상세 정보</h3>
                    <pre class="text-xs opacity-70 whitespace-pre-wrap">
                      {JSON.stringify(cut, null, 2)}
                    </pre>
                  </div>
                {/if}
              </div>
            {/each}
          </div>
          </div>
        </div>
      {/each}
    </div>
    
    <!-- Action Buttons -->
    <div class="flex justify-end mt-8">
      <button onclick={() => goto('/video/images')} class="btn btn-primary">다음 단계로</button>
    </div>
  {/if}
</div>