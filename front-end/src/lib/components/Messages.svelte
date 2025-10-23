<script lang="ts">
    import { errorMessage, successMessage } from "$lib/stores";
</script>

<!-- Success Message -->
{#if $successMessage}
    <div class="toast toast-bottom z-[9999]">
        <div class="alert alert-success">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span>{$successMessage}</span>
        </div>
    </div>
{/if}

<!-- Error Message -->
{#if $errorMessage}
    <div class="toast toast-bottom z-[9999]">
        <div class="alert alert-error">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <span>{$errorMessage}</span>
        </div>
    </div>
{/if}
