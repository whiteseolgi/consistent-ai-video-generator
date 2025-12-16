<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { api } from "$lib/api";
    import { projectState, cuts, selectedCuts, cutImages, setLoading, showSuccess, showError, getCutId } from "$lib/stores";
    import CutCard from "$lib/components/CutCard.svelte";
    import type { ImageModel, ImageStyle, ImageQuality, ImageSize } from "$lib/types";

    let imageModel: ImageModel = $projectState.default_image_model;
    let imageStyle: ImageStyle = $projectState.default_image_style;
    let imageQuality: ImageQuality = $projectState.default_image_quality;
    let imageSize: ImageSize = $projectState.default_image_size;

    const imageModels: ImageModel[] = ["gpt-image-1", "gemini-2.5-flash-imag(Nano Banana)", "gemini-3-pro-image-preview(Nano Banana Pro)"];
    const imageStyles: ImageStyle[] = ["realistic", "illustration", "anime", "watercolor", "oil_painting", "comic", "storybook", "sketch", "pixel_art", "lowpoly"];
    const imageQualities: ImageQuality[] = ["low", "medium", "high"];
    const imageSizes: ImageSize[] = ["1024x1024", "1536x1024", "2048x2048"];

    // Load existing cuts on mount
    onMount(async () => {
        if ($projectState.work_dir && $projectState.entity_set_name) {
            const loadedCuts = await api.loadCuts($projectState.work_dir, $projectState.entity_set_name);
            if (loadedCuts && loadedCuts.length > 0) {
                cuts.set(loadedCuts);
            }
        }
    });

    function toggleCut(sceneNum: number, cutNum: number) {
        const cutId = getCutId(sceneNum, cutNum);
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

    function selectAll() {
        const allCutIds = new Set<string>();
        $cuts.forEach((sceneCuts, sceneIndex) => {
            sceneCuts.forEach((_, cutIndex) => {
                allCutIds.add(getCutId(sceneIndex + 1, cutIndex + 1));
            });
        });
        selectedCuts.set(allCutIds);
    }

    function deselectAll() {
        selectedCuts.set(new Set());
    }

    async function generateImages() {
        if ($selectedCuts.size === 0) {
            showError("생성할 컷을 선택해주세요");
            return;
        }

        setLoading(true, `${$selectedCuts.size}개 컷 이미지 생성 중...`);

        try {
            // Convert selected cuts to scene and cut numbers
            const selectedCutsList = Array.from($selectedCuts)
                .map((cutId) => {
                    const match = cutId.match(/S(\d+)-C(\d+)/);
                    if (match) {
                        return {
                            scene_num: parseInt(match[1]),
                            cut_num: parseInt(match[2]),
                        };
                    }
                    return null;
                })
                .filter(Boolean);

            // Generate images for selected cuts
            const result = await api.generateCutImages({
                entity_set_name: $projectState.entity_set_name,
                work_dir: $projectState.work_dir,
                image_model: imageModel,
                image_style: imageStyle,
                image_quality: imageQuality,
                image_size: imageSize,
                selected_cuts: selectedCutsList,
            });

            // Store image paths
            const imageMap = new Map<string, string>();
            result.cut_image_paths.forEach((path, index) => {
                // Extract scene and cut numbers from filename
                const filename = path.split("/").pop() || "";
                const match = filename.match(/S(\d+)-C(\d+)/);
                if (match) {
                    const cutId = getCutId(parseInt(match[1]), parseInt(match[2]));
                    imageMap.set(cutId, path);
                }
            });
            cutImages.set(imageMap);

            showSuccess("컷 이미지 생성 완료");
            goto("/video/storyboard");
        } catch (error) {
            showError("이미지 생성 중 오류가 발생했습니다");
            console.error(error);
        } finally {
            setLoading(false);
        }
    }
</script>

<div class="max-w-5xl mx-auto">
    <h1 class="text-3xl font-bold mb-8 text-white">컷 이미지 생성</h1>

    {#if $cuts.length === 0}
        <div class="card bg-base-100 shadow">
            <div class="card-body items-center text-center">
                <p class="opacity-70 mb-4">아직 분석된 컷이 없습니다.</p>
                <button onclick={() => goto("/story/review")} class="btn btn-primary">씬/컷 확인으로 이동</button>
            </div>
        </div>
    {:else}
        <!-- Selection Controls -->
        <div class="card bg-base-100 shadow mb-6">
            <div class="card-body p-4 flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <button onclick={selectAll} class="btn btn-sm">전체 선택</button>
                    <button onclick={deselectAll} class="btn btn-sm btn-ghost">전체 해제</button>
                    <span class="text-sm opacity-70">
                        {$selectedCuts.size}개 선택됨
                    </span>
                </div>

                <!-- Model Settings -->
                <div class="flex items-center gap-3">
                    <select bind:value={imageModel} class="select select-bordered" style="min-width: 200px;">
                        {#each imageModels as model}
                            <option value={model}>{model}</option>
                        {/each}
                    </select>

                    <select bind:value={imageStyle} class="select select-bordered" style="min-width: 180px;">
                        {#each imageStyles as style}
                            <option value={style}>{style}</option>
                        {/each}
                    </select>

                    <select bind:value={imageQuality} class="select select-bordered" style="min-width: 120px;">
                        {#each imageQualities as quality}
                            <option value={quality}>{quality}</option>
                        {/each}
                    </select>
                </div>
            </div>
        </div>

        <!-- Cuts List -->
        <div class="space-y-8">
            {#each $cuts as sceneCuts, sceneIndex}
                <div class="card bg-base-100 shadow">
                    <div class="card-body">
                        <h2 class="text-xl font-semibold mb-4">
                            씬 {sceneIndex + 1}
                        </h2>

                        <div class="space-y-3">
                            {#each sceneCuts as cut, cutIndex}
                                {@const cutId = getCutId(sceneIndex + 1, cutIndex + 1)}
                                {@const isSelected = $selectedCuts.has(cutId)}
                                <div class="flex items-start gap-3 cursor-pointer" onclick={() => toggleCut(sceneIndex + 1, cutIndex + 1)}>
                                    <input type="checkbox" checked={isSelected} onchange={(e) => e.stopPropagation()} class="checkbox checkbox-primary mt-5" />
                                    <div class="flex-1">
                                        <CutCard sceneNum={sceneIndex + 1} cutNum={cutIndex + 1} {cut} />
                                    </div>
                                </div>
                            {/each}
                        </div>
                    </div>
                </div>
            {/each}
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end mt-8">
            <button onclick={generateImages} disabled={$selectedCuts.size === 0} class="btn btn-primary disabled:btn-disabled">이미지 생성</button>
        </div>
    {/if}
</div>
