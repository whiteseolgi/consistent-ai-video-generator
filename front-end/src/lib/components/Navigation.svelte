<script lang="ts">
  import { page } from '$app/stores';
  import { currentStep, projectState, showApiLogs } from '$lib/stores';
  
  type Step = { id: number; name: string; path: string };
  const steps: Step[] = [
    { id: 0, name: '시작', path: '/' },
    { id: 1, name: '레퍼런스', path: '/reference/synopsis' },
    { id: 2, name: '스토리', path: '/story/input' },
    { id: 3, name: '영상 생성', path: '/video/images' }
  ];

  const submenus: Record<number, Step[]> = {
    1: [
      { id: 11, name: '시놉시스 분석', path: '/reference/synopsis' },
      { id: 12, name: '엔티티 관리', path: '/reference/entities' }
    ],
    2: [
      { id: 21, name: '스토리 입력', path: '/story/input' },
      { id: 22, name: '씬/컷 확인', path: '/story/review' }
    ],
    3: [
      { id: 31, name: '컷 이미지', path: '/video/images' },
      { id: 32, name: '스토리보드', path: '/video/storyboard' },
      { id: 33, name: '영상 확인', path: '/video/review' },
      { id: 34, name: '최종 영상', path: '/video/final' }
    ]
  };
  
  $: currentPath = $page.url.pathname;
  function getCurrentStep(path: string): number {
    if (path.startsWith('/video')) return 3;
    if (path.startsWith('/story')) return 2;
    if (path.startsWith('/reference')) return 1;
    return 0;
  }
  $: $currentStep = getCurrentStep(currentPath);
</script>

<nav class="bg-base-100 shadow" style="margin-top: 60px;">
  <div class="container mx-auto px-4 md:px-6 py-3 space-y-3">
    <!-- Top row: centered brand/project, log toggle right -->
    <div class="grid grid-cols-3 items-center">
      <div></div>
      <div class="text-center">
        <a href="/" class="btn btn-ghost text-xl">CAVG</a>
        {#if $projectState.entity_set_name}
          <span class="ml-2 align-middle text-sm opacity-70 truncate inline-block max-w-[40vw] md:max-w-xs">
            프로젝트: {$projectState.entity_set_name}
          </span>
        {/if}
      </div>
      <div class="flex justify-end" style="position: absolute; right: 0;">
        <button onclick={() => showApiLogs.update(v => !v)} class="btn btn-sm btn-ghost">
          {$showApiLogs ? '로그 숨기기' : '로그 보기'}
        </button>
      </div>
    </div>

    <!-- Main steps as button group (centered) -->
    <div class="hidden md:flex justify-center">
      <div class="btn-group">
        {#each steps as step, i}
          <a href={step.path} class={`btn btn-md ${i === $currentStep ? 'btn-primary' : 'btn-ghost'}`}>{step.name}</a>
        {/each}
      </div>
    </div>

    <!-- Mobile: horizontal scroll buttons (truly centered) -->
    <div class="md:hidden overflow-x-auto flex justify-center">
      <div class="join flex justify-center w-full max-w-full">
        {#each steps as step, i}
          <a href={step.path} class={`btn btn-sm join-item ${i === $currentStep ? 'btn-primary' : 'btn-ghost'}`}>{step.name}</a>
        {/each}
      </div>
    </div>

    <!-- Sub menu row (centered) -->
    {#if submenus[$currentStep]}
      <div class="flex justify-center" style="margin-bottom: 12px;">
        <div class="tabs tabs-boxed">
          {#each submenus[$currentStep] as item}
            <a href={item.path} class={`tab tab-sm md:tab-md ${currentPath.startsWith(item.path) ? 'tab-active' : ''}`}>{item.name}</a>
          {/each}
        </div>
      </div>
    {/if}
  </div>
</nav>