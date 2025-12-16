<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { api } from "$lib/api";
    import { projectState, showSuccess, showError } from "$lib/stores";
    import type { TextModel, ImageModel, VideoModel, ImageStyle, ImageQuality, ImageSize } from "$lib/types";

    let workDir = $projectState.work_dir;
    let entitySetName = $projectState.entity_set_name;
    let defaultTextModel = $projectState.default_text_model;
    let defaultImageModel = $projectState.default_image_model;
    let defaultVideoModel = $projectState.default_video_model;
    let defaultImageStyle = $projectState.default_image_style;
    let defaultImageQuality = $projectState.default_image_quality;
    let defaultImageSize = $projectState.default_image_size;

    const textModels: TextModel[] = ["gpt-4.1", "gpt-4o", "gpt-5", "gpt-5.1"];
    const imageModels: ImageModel[] = ["gpt-image-1", "gemini-2.5-flash-imag(Nano Banana)", "gemini-3-pro-image-preview(Nano Banana Pro)"];
    const videoModels: VideoModel[] = ["runway", "sora2", "veo-3.0-fast-generate-001", "veo-3.0-generate-001", "veo-3.1-fast-generate-preview", "veo-3.1-generate-preview"];
    const imageStyles: ImageStyle[] = ["realistic", "illustration", "anime", "watercolor", "oil_painting", "comic", "storybook", "sketch", "pixel_art", "lowpoly"];
    const imageQualities: ImageQuality[] = ["low", "medium", "high"];
    const imageSizes: ImageSize[] = ["1024x1024", "1536x1024", "2048x2048"];

    let existingEntitySets: string[] = [];

    // Load existing projects when work dir changes
    $: if (workDir) {
        loadProjects();
    }

    async function loadProjects() {
        if (workDir) {
            const projects = await api.listProjects(workDir);
            existingEntitySets = projects;
        }
    }

    function startProject() {
        if (!workDir) {
            showError("작업 디렉토리를 입력해주세요");
            return;
        }

        if (!entitySetName) {
            showError("프로젝트 이름을 입력해주세요");
            return;
        }

        projectState.set({
            work_dir: workDir,
            entity_set_name: entitySetName,
            default_text_model: defaultTextModel,
            default_image_model: defaultImageModel,
            default_video_model: defaultVideoModel,
            default_image_style: defaultImageStyle,
            default_image_quality: defaultImageQuality,
            default_image_size: defaultImageSize,
        });

        showSuccess("프로젝트 설정이 저장되었습니다");
        goto("/reference/synopsis");
    }
</script>

<div class="max-w-2xl mx-auto">
    <h1 class="text-3xl font-bold mb-8 text-white">새 프로젝트 시작</h1>

    <div class="card bg-base-100 shadow">
        <div class="card-body space-y-6">
            <!-- Work Directory -->
            <div>
                <label for="workDir" class="label">
                    <span class="label-text">서버 경로</span>
                </label>
                <input id="workDir" type="text" bind:value={workDir} placeholder="/path/to/work/directory" class="input input-bordered w-full box-border" />
            </div>

            <!-- Entity Set Name -->
            <div>
                <label for="entitySetName" class="label">
                    <span class="label-text">프로젝트 이름</span>
                </label>
                <div class="flex gap-2">
                    <input id="entitySetName" type="text" bind:value={entitySetName} placeholder="my-video-project" class="input input-bordered flex-1" />
                    {#if existingEntitySets.length > 0}
                        <select onchange={(e) => (entitySetName = e.currentTarget.value)} class="select select-bordered">
                            <option value="">기존 프로젝트 선택</option>
                            {#each existingEntitySets as set}
                                <option value={set}>{set}</option>
                            {/each}
                        </select>
                    {/if}
                </div>
            </div>

            <!-- Default Models Section -->
            <div class="divider">기본 AI 모델 설정</div>

            <div class="grid grid-cols-2 gap-4">
                <!-- Text Model -->
                <div>
                    <label for="textModel" class="label"><span class="label-text">텍스트 모델</span></label>
                    <select id="textModel" bind:value={defaultTextModel} class="select select-bordered w-full">
                        {#each textModels as model}
                            <option value={model}>{model}</option>
                        {/each}
                    </select>
                </div>

                <!-- Image Model -->
                <div>
                    <label for="imageModel" class="label"><span class="label-text">이미지 모델</span></label>
                    <select id="imageModel" bind:value={defaultImageModel} class="select select-bordered w-full">
                        {#each imageModels as model}
                            <option value={model}>{model}</option>
                        {/each}
                    </select>
                </div>

                <!-- Video Model -->
                <div>
                    <label for="videoModel" class="label"><span class="label-text">비디오 모델</span></label>
                    <select id="videoModel" bind:value={defaultVideoModel} class="select select-bordered w-full">
                        {#each videoModels as model}
                            <option value={model}>{model}</option>
                        {/each}
                    </select>
                </div>

                <!-- Image Style -->
                <div>
                    <label for="imageStyle" class="label"><span class="label-text">이미지 스타일</span></label>
                    <select id="imageStyle" bind:value={defaultImageStyle} class="select select-bordered w-full">
                        {#each imageStyles as style}
                            <option value={style}>{style}</option>
                        {/each}
                    </select>
                </div>

                <!-- Image Quality -->
                <div>
                    <label for="imageQuality" class="label"><span class="label-text">이미지 품질</span></label>
                    <select id="imageQuality" bind:value={defaultImageQuality} class="select select-bordered w-full">
                        {#each imageQualities as quality}
                            <option value={quality}>{quality}</option>
                        {/each}
                    </select>
                </div>

                <!-- Image Size -->
                <div>
                    <label for="imageSize" class="label"><span class="label-text">이미지 크기</span></label>
                    <select id="imageSize" bind:value={defaultImageSize} class="select select-bordered w-full">
                        {#each imageSizes as size}
                            <option value={size}>{size}</option>
                        {/each}
                    </select>
                </div>
            </div>

            <!-- Start Button -->
            <div class="card-actions justify-end">
                <button onclick={startProject} class="btn btn-primary">프로젝트 시작</button>
            </div>
        </div>
    </div>
</div>
