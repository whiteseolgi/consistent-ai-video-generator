<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import { entityList, projectState } from '$lib/stores';
  import EntityCard from '$lib/components/EntityCard.svelte';
  import EntityEditModal from '$lib/components/EntityEditModal.svelte';
  import type { EntityTuple, EntityType } from '$lib/types';
  
  let showEditModal = false;
  let editingEntity: EntityTuple | null = null;
  let editingIndex: number | null = null;
  let isAddMode = false;
  
  // Load existing entities on mount
  onMount(async () => {
    console.log('🚀 Entity page onMount started');
    console.log('Project state:', $projectState);
    console.log('API debug info:', api.getDebugInfo());
    
    if ($projectState.work_dir && $projectState.entity_set_name) {
      try {
        console.log('🔄 Loading entity list...');
        const entities = await api.loadEntityList($projectState.work_dir, $projectState.entity_set_name);
        console.log('📥 Received entities:', entities);
        
        if (entities && entities.length > 0) {
          entityList.set(entities);
          console.log('✅ Entity list set successfully');
        } else {
          console.log('⚠️ No entities found or empty list');
        }
      } catch (error) {
        console.error('❌ Failed to load entity list:', error);
      }
    } else {
      console.log('⚠️ Missing project state:', {
        work_dir: $projectState.work_dir,
        entity_set_name: $projectState.entity_set_name
      });
    }
  });
  
  // Group entities by type
  $: characters = $entityList.filter(e => e[0] === 'character' && e[1] !== '기타');
  $: locations = $entityList.filter(e => e[0] === 'location' && e[1] !== '기타');
  $: objects = $entityList.filter(e => e[0] === 'object' && e[1] !== '기타');
  
  function openEditModal(entity: EntityTuple, index: number) {
    editingEntity = entity;
    editingIndex = index;
    isAddMode = false;
    showEditModal = true;
  }
  
  function openAddModal(type: EntityType) {
    editingEntity = [type, '', '', null];
    editingIndex = null;
    isAddMode = true;
    showEditModal = true;
  }
  
  function closeModal() {
    showEditModal = false;
    editingEntity = null;
    editingIndex = null;
    isAddMode = false;
  }
  
</script>

<div class="max-w-6xl mx-auto">
  <h1 class="text-3xl font-bold text-white mb-8">레퍼런스 확인 및 수정</h1>
  
  {#if $entityList.length === 0}
    <div class="bg-white rounded-lg shadow-md p-12 text-center">
      <p class="text-gray-600 mb-4">아직 생성된 레퍼런스가 없습니다.</p>
      <button
        onclick={() => goto('/reference/synopsis')}
        class="btn btn-primary"
      >
        시놉시스 분석으로 이동
      </button>
    </div>
  {:else}
    <!-- Characters Section -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">인물</h2>
      <div class="flex gap-4 overflow-x-auto pb-4">
        {#each characters as entity, index (index)}
          <EntityCard
            {entity}
            {index}
            onclick={() => openEditModal(entity, $entityList.indexOf(entity))}
          />
        {/each}
        
        <!-- Add Button -->
        <button
          onclick={() => openAddModal('character')}
          class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer overflow-hidden flex-shrink-0 h-64 flex flex-col items-center justify-center text-gray-400 hover:text-gray-600"
          style="width: 300px; background-color: #ffffff; border: none;"
        >
          <svg class="w-6 h-6 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" width="100px" height="100px">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>인물 추가</span>
        </button>
      </div>
    </div>
    
    <!-- Locations Section -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">배경</h2>
      <div class="flex gap-4 overflow-x-auto pb-4">
        {#each locations as entity, index (index)}
          <EntityCard
            {entity}
            {index}
            onclick={() => openEditModal(entity, $entityList.indexOf(entity))}
          />
        {/each}
        
        <!-- Add Button -->
        <button
          onclick={() => openAddModal('location')}
          class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer overflow-hidden flex-shrink-0 h-64 flex flex-col items-center justify-center text-gray-400 hover:text-gray-600"
          style="width: 300px; background-color: #ffffff; border: none;"
        >
          <svg class="w-6 h-6 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"  width="100px" height="100px">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>배경 추가</span>
        </button>
      </div>
    </div>
    
    <!-- Objects Section -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">사물</h2>
      <div class="flex gap-4 overflow-x-auto pb-4">
        {#each objects as entity, index (index)}
          <EntityCard
            {entity}
            {index}
            onclick={() => openEditModal(entity, $entityList.indexOf(entity))}
          />
        {/each}
        
        <!-- Add Button -->
        <button
          onclick={() => openAddModal('object')}
          class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer overflow-hidden flex-shrink-0 h-64 flex flex-col items-center justify-center text-gray-400 hover:text-gray-600"
          style="width: 300px; background-color: #ffffff; border: none;"
        >
          <svg class="w-6 h-6 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" width="100px" height="100px">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>사물 추가</span>
        </button>
      </div>
    </div>
    
    <!-- Action Buttons -->
    <div class="flex justify-end">
      <button
        onclick={() => goto('/story/input')}
        class="btn btn-primary"
      >
        다음 단계로
      </button>
    </div>
  {/if}
</div>

<!-- Edit Modal -->
{#if showEditModal && editingEntity}
  <EntityEditModal
    entity={editingEntity}
    index={editingIndex}
    isAdd={isAddMode}
    onclose={closeModal}
  />
{/if}
