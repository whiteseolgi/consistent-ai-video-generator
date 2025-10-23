<script lang="ts">
  import { apiLogs, showApiLogs } from '$lib/stores';
  import type { ApiLogEntry } from '$lib/types';
  
  function formatTime(date: Date): string {
    return date.toLocaleTimeString('ko-KR');
  }
  
  function getStatusColor(status: ApiLogEntry['status']): string {
    switch (status) {
      case 'pending': return 'text-yellow-600';
      case 'success': return 'text-green-600';
      case 'error': return 'text-red-600';
      default: return 'text-gray-600';
    }
  }
</script>

<div class="fixed bottom-0 left-0 right-0 bg-base-100 border-t border-base-200 shadow-lg transition-transform {$showApiLogs ? 'translate-y-0' : 'translate-y-full'}">
  <div class="container mx-auto px-4 py-2">
    <div class="flex items-center justify-between mb-2">
      <h3 class="text-sm font-semibold">API 로그</h3>
      <div class="flex items-center gap-2">
        <button onclick={() => apiLogs.clear()} class="btn btn-ghost btn-xs">Clear</button>
        <button onclick={() => showApiLogs.set(false)} class="btn btn-ghost btn-xs" aria-label="close logs">
          ✕
        </button>
      </div>
    </div>

    <div class="max-h-48 overflow-y-auto">
      <table class="table table-zebra table-xs">
        <thead>
          <tr>
            <th>시간</th>
            <th>엔드포인트</th>
            <th>메소드</th>
            <th>상태</th>
            <th>메시지</th>
          </tr>
        </thead>
        <tbody>
          {#each $apiLogs as log (log.id)}
            <tr>
              <td>{formatTime(log.timestamp)}</td>
              <td class="font-mono">{log.endpoint}</td>
              <td>{log.method}</td>
              <td class="font-medium {getStatusColor(log.status)}">{log.status}</td>
              <td>{log.message || log.error || '-'}</td>
            </tr>
          {/each}
        </tbody>
      </table>

      {#if $apiLogs.length === 0}
        <div class="py-4 text-center text-sm opacity-60">No API logs yet</div>
      {/if}
    </div>
  </div>
</div>