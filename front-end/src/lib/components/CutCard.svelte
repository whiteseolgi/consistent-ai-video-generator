<script lang="ts">
  import type { Cut } from '$lib/types';
  
  export let sceneNum: number;
  export let cutNum: number;
  export let cut: Cut;
  export let expanded: boolean = false;
  export let onclick: () => void = () => {};
</script>

<button {onclick} class="w-full text-left card bg-base-100 shadow hover:shadow-lg transition-shadow">
  <div class="card-body p-4">
  <div class="flex items-start justify-between">
    <div class="flex-1">
      <div class="flex items-center gap-3 mb-2">
        <span class="badge badge-neutral badge-sm">
          S{sceneNum.toString().padStart(2, '0')}-C{cutNum.toString().padStart(2, '0')}
        </span>
        {#if cut.entities && cut.entities.length > 0}
          <div class="flex flex-wrap gap-1">
            {#each cut.entities as entity}
              <span class="badge badge-outline badge-sm">
                {entity}
              </span>
            {/each}
          </div>
        {/if}
      </div>
      <p class="text-sm md:text-base {expanded ? '' : 'line-clamp-2'}">
        {cut.description}
      </p>
    </div>
    <div class="flex items-center justify-center w-6 h-6 flex-shrink-0">
      <svg
        class="w-3 h-3 opacity-60 transition-transform {expanded ? 'rotate-180' : ''}"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </div>
  </div>
  </div>
</button>