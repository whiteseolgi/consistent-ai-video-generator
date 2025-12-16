<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import { projectState, scenes, cuts, setLoading, showSuccess, showError } from '$lib/stores';
  import type { TextModel } from '$lib/types';
  
  let storyText = '';
  let fileInput: HTMLInputElement;
  let textModel: TextModel = $projectState.default_text_model;
  
  const textModels: TextModel[] = ['gpt-4.1', 'gpt-4o', 'gpt-5', 'gpt-5.1'];
  
  // Load existing story or synopsis text if available
  onMount(async () => {
    if ($projectState.work_dir && $projectState.entity_set_name) {
      const result = await api.loadStoryText($projectState.work_dir, $projectState.entity_set_name);
      if (result.text) {
        storyText = result.text;
      }
    }
  });
  
  function handleFileSelect(event: Event) {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        storyText = e.target?.result as string;
      };
      reader.readAsText(file);
    }
  }
  
  async function analyzeStory() {
    if (!storyText.trim()) {
      showError('스토리 텍스트를 입력해주세요');
      return;
    }
    
    setLoading(true, '스토리 분석 중...');
    
    try {
      // 1. Generate scenes
      const scenesResult = await api.generateScenes({
        entity_set_name: $projectState.entity_set_name,
        work_dir: $projectState.work_dir,
        story_text: storyText,
        text_model: textModel
      });
      
      scenes.set(scenesResult.scenes);
      
      setLoading(true, '컷 생성 중...');
      
      // 2. Generate cuts
      const cutsResult = await api.generateCuts({
        entity_set_name: $projectState.entity_set_name,
        work_dir: $projectState.work_dir,
        scenes: scenesResult.scenes,
        story_text: storyText,
        text_model: textModel
      });
      
      cuts.set(cutsResult.cut_list);
      
      showSuccess('스토리 분석 완료');
      goto('/story/review');
    } catch (error) {
      showError('스토리 분석 중 오류가 발생했습니다');
      console.error(error);
    } finally {
      setLoading(false);
    }
  }
</script>

<div class="mx-auto">
  <h1 class="text-3xl font-bold mb-8 text-white">스토리 입력 및 분석</h1>

  <div class="card bg-base-100 shadow">
    <div class="card-body space-y-6">
      <!-- Story Text Input -->
      <div class="form-control">
        <label for="story" class="label">
          <span class="label-text">스토리 텍스트</span>
        </label>
        <textarea
          id="story"
          bind:value={storyText}
          rows="15"
          placeholder="스토리를 입력하세요..."
          class="textarea textarea-bordered w-full h-64 md:h-72 box-border"
        ></textarea>
      </div>

      <!-- File Upload -->
      <div class="form-control">
        <input
          type="file"
          accept=".txt"
          bind:this={fileInput}
          onchange={handleFileSelect}
          class="file-input file-input-bordered w-full max-w-xs box-border"
        />
        <div class="label hidden">
          <span class="label-text-alt">TXT 파일을 선택하세요</span>
        </div>
      </div>

      <!-- Model Settings -->
      <div class="divider">AI 모델 설정</div>
      <div class="form-control w-full max-w-xs">
        <label for="textModel" class="label">
          <span class="label-text">텍스트 모델</span>
        </label>
        <select
          id="textModel"
          bind:value={textModel}
          class="select select-bordered"
        >
          {#each textModels as model}
            <option value={model}>{model}</option>
          {/each}
        </select>
      </div>

      <!-- Action Buttons -->
      <div class="card-actions justify-end mt-4">
        <button onclick={() => goto('/story/review')} class="btn btn-ghost">
          건너뛰기
        </button>
        <button onclick={analyzeStory} class="btn btn-primary">
          씬/컷 분석
        </button>
      </div>
    </div>
  </div>
</div>