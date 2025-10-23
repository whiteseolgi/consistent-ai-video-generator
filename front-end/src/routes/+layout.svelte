<script lang="ts">
    import "../app.css";
    import { showApiLogs } from "$lib/stores";
    import Navigation from "$lib/components/Navigation.svelte";
    import ApiLogs from "$lib/components/ApiLogs.svelte";
    import LoadingOverlay from "$lib/components/LoadingOverlay.svelte";
    import Messages from "$lib/components/Messages.svelte";

    let { children } = $props();
</script>

<svelte:head>
    <title>Consistent AI Video Generator</title>
</svelte:head>

<div class="min-h-screen flex flex-col bg-base-100">
    <!-- Header Banner -->
    <div style="background-color: #1a1a1a; color: white; padding: 12px 0; margin: 0; position: fixed; top: 0; left: 0; right: 0; z-index: 1000;">
        <div class="container mx-auto px-4 md:px-6">
            <div class="text-center">
                <span style="color: white; font-weight: bold; font-size: 28px; margin-right: 12px;">백설기</span>
                <span style="color: #9ca3af; font-size: 24px; margin: 0 8px;">|</span>
                <span style="color: white; font-size: 20px; margin-left: 12px;">영상 구성 객체(인물, 사물, 배경)의 일관성을 유지한 AI 영상 자동 생성 서비스</span>
                <span class="lg:inline">
                    <span style="color: #9ca3af; font-size: 18px; margin: 0 12px;"> </span>
                    <span style="color: #d1d5db; font-size: 18px;">Consistent AI Video Generator</span>
                </span>
            </div>
        </div>
    </div>

    <!-- Navigation -->
    <Navigation />

    <!-- Main Content -->
    <main class="flex-1 container mx-auto px-4 md:px-6 py-6 md:py-10 cavg-background-image-filter">
        <div class="max-w-[1280px] mx-auto" style="padding: 10px;">
            {@render children?.()}
        </div>
    </main>

    <!-- API Logs -->
    {#if $showApiLogs}
        <ApiLogs />
    {/if}

    <!-- Loading Overlay -->
    <LoadingOverlay />

    <!-- Messages -->
    <Messages />
</div>
