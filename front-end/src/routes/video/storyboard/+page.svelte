<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { api } from "$lib/api";
    import { projectState, cuts, cutImages, selectedCuts, setLoading, showSuccess, showError, getCutId } from "$lib/stores";
    import type { VideoModel } from "$lib/types";

    let videoModel: VideoModel = $projectState.default_video_model;
    const videoModels: VideoModel[] = ["runway", "sora2", "veo-3.0-fast-generate-001", "veo-3.0-generate-001", "veo-3.1-fast-generate-preview", "veo-3.1-generate-preview"];

    // Load existing cut images and cuts on mount
    onMount(async () => {
        if ($projectState.work_dir && $projectState.entity_set_name) {
            // Load cuts first
            const loadedCuts = await api.loadCuts($projectState.work_dir, $projectState.entity_set_name);
            if (loadedCuts && loadedCuts.length > 0) {
                cuts.set(loadedCuts);
            }

            // Then load cut images
            const images = await api.loadCutImages($projectState.work_dir, $projectState.entity_set_name);
            if (images && images.length > 0) {
                const imageMap = new Map<string, string>();
                // Use Promise.all to generate all URLs asynchronously
                const urlPromises = images.map(async (img) => {
                    const cutId = getCutId(img.scene_num, img.cut_num);
                    try {
                        const imageUrl = await api.getImageUrlAsync($projectState.work_dir, $projectState.entity_set_name, img.path);
                        return { cutId, imageUrl };
                    } catch (error) {
                        console.error("Failed to generate image URL for", cutId, error);
                        // Fallback to synchronous method
                        const imageUrl = api.getImageUrl($projectState.work_dir, $projectState.entity_set_name, img.path);
                        return { cutId, imageUrl };
                    }
                });

                const urlResults = await Promise.all(urlPromises);
                urlResults.forEach(({ cutId, imageUrl }) => {
                    imageMap.set(cutId, imageUrl);
                });
                cutImages.set(imageMap);
                console.log("Cut images loaded:", imageMap.size);
            }
        }
    });

    function selectAll() {
        selectedCuts.set(new Set($cutImages.keys()));
    }

    function deselectAll() {
        selectedCuts.set(new Set());
    }

    function toggleImage(cutId: string) {
        selectedCuts.update((set) => {
            const newSet = new Set(set);
            if (newSet.has(cutId)) {
                newSet.delete(cutId);
            } else {
                newSet.add(cutId);
            }
            return newSet;
        });
    }

    async function generateVideos() {
        if ($selectedCuts.size === 0) {
            showError("생성할 이미지를 선택해주세요");
            return;
        }

        setLoading(true, `${$selectedCuts.size}개 영상 생성 중...`);

        try {
            // Convert selected cuts to image paths
            const selectedImagePaths = Array.from($selectedCuts)
                .map((cutId) => {
                    const imagePath = $cutImages.get(cutId);
                    if (imagePath) {
                        // Extract relative path from URL
                        const url = new URL(imagePath);
                        const params = new URLSearchParams(url.search);
                        return params.get("relative_path");
                    }
                    return null;
                })
                .filter(Boolean);

            const result = await api.generateCutVideos({
                entity_set_name: $projectState.entity_set_name,
                work_dir: $projectState.work_dir,
                video_model: videoModel,
                cut_image_paths: selectedImagePaths,
            });

            showSuccess("영상 생성 완료");
            goto("/video/review");
        } catch (error) {
            showError("영상 생성 중 오류가 발생했습니다");
            console.error(error);
        } finally {
            setLoading(false);
        }
    }
</script>

<div class="max-w-6xl mx-auto">
    <h1 class="text-3xl font-bold mb-8 text-white">스토리보드 - 컷 영상 생성</h1>

    <!-- Controls -->
    <div class="card bg-base-100 shadow mb-6">
        <div class="card-body p-4 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <button onclick={selectAll} class="btn btn-sm">전체 선택</button>
                <button onclick={deselectAll} class="btn btn-sm btn-ghost">전체 해제</button>
                <span class="text-sm opacity-70">{$selectedCuts.size}개 선택됨</span>
            </div>

            <div class="flex items-center gap-3">
                <label for="videoModel" class="label"><span class="label-text">비디오 모델</span></label>
                <select id="videoModel" bind:value={videoModel} class="select select-bordered">
                    {#each videoModels as model}
                        <option value={model}>{model}</option>
                    {/each}
                </select>
            </div>
        </div>
    </div>

    <!-- Storyboard Grid -->
    <div class="grid grid-cols-4 gap-4">
        {#each $cuts as sceneCuts, sceneIndex}
            {#each sceneCuts as cut, cutIndex}
                {@const cutId = getCutId(sceneIndex + 1, cutIndex + 1)}
                {@const imagePath = $cutImages.get(cutId)}
                {@const isSelected = $selectedCuts.has(cutId)}

                {#if imagePath}
                    <div class="relative card bg-base-100 shadow overflow-hidden cursor-pointer" onclick={() => toggleImage(cutId)}>
                        <input type="checkbox" checked={isSelected} onchange={(e) => e.stopPropagation()} class="absolute top-2 left-2 z-10 checkbox checkbox-primary" />
                        <img src={imagePath} alt={cutId} class="w-full h-36 md:h-48 object-cover" />
                        <div class="p-3">
                            <p class="text-sm font-semibold">{cutId}</p>
                            <p class="text-xs opacity-70 line-clamp-2">{cut.description}</p>
                        </div>
                    </div>
                {/if}
            {/each}
        {/each}
    </div>

    <!-- Actions -->
    <div class="flex justify-end mt-8">
        <button onclick={generateVideos} disabled={$selectedCuts.size === 0} class="btn btn-primary"> 영상 생성 </button>
    </div>
</div>
