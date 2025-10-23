<script lang="ts">
    import { isLoading, loadingMessage } from "$lib/stores";
</script>

{#if $isLoading}
    <div class="fixed top-4 left-1/2 transform -translate-x-1/2 z-[9999]">
        <div class="card bg-base-100 shadow-xl p-6 max-w-sm w-full">
            <div class="flex flex-col items-center">
                <!-- DaisyUI Spinner -->
                <span class="loading loading-spinner loading-lg text-primary mb-4"></span>

                <!-- Loading Message -->
                <p class="text-base-content text-center">
                    {$loadingMessage || "처리 중..."}
                </p>
            </div>
        </div>
    </div>
{/if}
