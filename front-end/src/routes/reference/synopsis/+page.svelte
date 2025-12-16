<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { api } from "$lib/api";
    import { projectState, setLoading, showSuccess, showError } from "$lib/stores";
    import type { TextModel, ImageModel, ImageStyle, ImageQuality, ImageSize } from "$lib/types";

    let synopsisText = "";
    let fileInput: HTMLInputElement;
    let textModel: TextModel = $projectState.default_text_model;
    let imageModel: ImageModel = $projectState.default_image_model;
    let imageStyle: ImageStyle = $projectState.default_image_style;
    let imageQuality: ImageQuality = $projectState.default_image_quality;
    let imageSize: ImageSize = $projectState.default_image_size;

    const textModels: TextModel[] = ["gpt-4.1", "gpt-4o", "gpt-5", "gpt-5.1"];
    const imageModels: ImageModel[] = ["gpt-image-1", "gemini-2.5-flash-imag(Nano Banana)", "gemini-3-pro-image-preview(Nano Banana Pro)"];
    const imageStyles: ImageStyle[] = ["realistic", "illustration", "anime", "watercolor", "oil_painting", "comic", "storybook", "sketch", "pixel_art", "lowpoly"];
    const imageQualities: ImageQuality[] = ["low", "medium", "high"];
    const imageSizes: ImageSize[] = ["1024x1024", "1536x1024", "2048x2048"];

    // Load existing synopsis text if available
    onMount(async () => {
        if ($projectState.work_dir && $projectState.entity_set_name) {
            const text = await api.loadSynopsisText($projectState.work_dir, $projectState.entity_set_name);
            if (text) {
                synopsisText = text;
            }
        }
    });

    function handleFileSelect(event: Event) {
        const target = event.target as HTMLInputElement;
        const file = target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                synopsisText = e.target?.result as string;
            };
            reader.readAsText(file);
        }
    }

    async function analyzeSynopsis() {
        if (!synopsisText.trim()) {
            showError("시놉시스 텍스트를 입력해주세요");
            return;
        }

        setLoading(true, "시놉시스 분석 중...");

        try {
            // 1. Analyze synopsis
            const analysisResult = await api.analyzeSynopsis({
                entity_set_name: $projectState.entity_set_name,
                work_dir: $projectState.work_dir,
                synopsis_text: synopsisText,
                text_model: textModel,
            });

            setLoading(true, "레퍼런스 이미지 생성 중...");

            // 2. Create entities
            const entitiesResult = await api.createEntities({
                entity_set_name: $projectState.entity_set_name,
                work_dir: $projectState.work_dir,
                entity_dict_draft_list: analysisResult.entity_dict_draft_list,
                image_model: imageModel,
                image_style: imageStyle,
                image_quality: imageQuality,
                image_size: imageSize,
            });

            showSuccess("시놉시스 분석 및 레퍼런스 생성 완료");
            goto("/reference/entities");
        } catch (error) {
            showError("시놉시스 분석 중 오류가 발생했습니다");
            console.error(error);
        } finally {
            setLoading(false);
        }
    }
</script>

<div class="mx-auto">
    <h1 class="text-3xl font-bold mb-8 text-white">시놉시스 분석 및 레퍼런스 생성</h1>

    <div class="card bg-base-100 shadow">
        <div class="card-body space-y-6">
            <!-- Synopsis Text Input -->
            <div class="form-control">
                <label for="synopsis" class="label">
                    <span class="label-text">시놉시스 텍스트</span>
                </label>
                <textarea id="synopsis" bind:value={synopsisText} rows="10" placeholder="시놉시스를 입력하세요..." class="textarea textarea-bordered w-full h-48 box-border"></textarea>
            </div>

            <!-- File Upload -->
            <div class="form-control">
                <input type="file" accept=".txt" bind:this={fileInput} onchange={handleFileSelect} class="file-input file-input-bordered w-full max-w-xs box-border" />
            </div>

            <!-- Model Settings -->
            <div class="divider">AI 모델 설정</div>

            <div class="grid grid-cols-2 gap-4">
                <!-- Text Model -->
                <div>
                    <label for="textModel" class="label"><span class="label-text">텍스트 모델</span></label>
                    <select id="textModel" bind:value={textModel} class="select select-bordered w-full">
                        {#each textModels as model}
                            <option value={model}>{model}</option>
                        {/each}
                    </select>
                </div>

                <!-- Image Model -->
                <div>
                    <label for="imageModel" class="label"><span class="label-text">이미지 모델</span></label>
                    <select id="imageModel" bind:value={imageModel} class="select select-bordered w-full">
                        {#each imageModels as model}
                            <option value={model}>{model}</option>
                        {/each}
                    </select>
                </div>

                <!-- Image Style -->
                <div>
                    <label for="imageStyle" class="label"><span class="label-text">화풍</span></label>
                    <select id="imageStyle" bind:value={imageStyle} class="select select-bordered w-full">
                        {#each imageStyles as style}
                            <option value={style}>{style}</option>
                        {/each}
                    </select>
                </div>

                <!-- Image Quality -->
                <div>
                    <label for="imageQuality" class="label"><span class="label-text">이미지 품질</span></label>
                    <select id="imageQuality" bind:value={imageQuality} class="select select-bordered w-full">
                        {#each imageQualities as quality}
                            <option value={quality}>{quality}</option>
                        {/each}
                    </select>
                </div>

                <!-- Image Size -->
                <div>
                    <label for="imageSize" class="label"><span class="label-text">이미지 크기</span></label>
                    <select id="imageSize" bind:value={imageSize} class="select select-bordered w-full">
                        {#each imageSizes as size}
                            <option value={size}>{size}</option>
                        {/each}
                    </select>
                </div>
            </div>
        </div>

        <!-- Action Buttons -->
        <div class="card-actions justify-end">
            <button onclick={() => goto("/reference/entities")} class="btn btn-ghost">건너뛰기</button>
            <button onclick={analyzeSynopsis} class="btn btn-primary">레퍼런스 생성</button>
        </div>
    </div>
</div>
