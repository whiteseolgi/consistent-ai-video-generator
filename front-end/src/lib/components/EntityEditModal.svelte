<script lang="ts">
    import { api } from "$lib/api";
    import { entityList, projectState, setLoading, showSuccess, showError } from "$lib/stores";
    import type { EntityTuple, EntityType, TextModel, ImageModel, ImageStyle, ImageQuality, ImageSize } from "$lib/types";

    export let entity: EntityTuple;
    export let index: number | null;
    export let isAdd: boolean;
    export let onclose: () => void;

    let [type, name, description, imagePath] = entity;
    let extraPrompt = "";
    let imageFile: File | null = null;
    let fileInput: HTMLInputElement;
    let videoRef: HTMLVideoElement;
    let canvasRef: HTMLCanvasElement;
    let showCamera = false;

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

    function handleFileSelect(event: Event) {
        const target = event.target as HTMLInputElement;
        const file = target.files?.[0];
        if (file) {
            imageFile = file;
        }
    }

    async function startCamera() {
        showCamera = true;
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            if (videoRef) {
                videoRef.srcObject = stream;
            }
        } catch (error) {
            showError("카메라 접근 권한이 필요합니다");
            showCamera = false;
        }
    }

    function capturePhoto() {
        if (videoRef && canvasRef) {
            const context = canvasRef.getContext("2d");
            if (context) {
                canvasRef.width = videoRef.videoWidth;
                canvasRef.height = videoRef.videoHeight;
                context.drawImage(videoRef, 0, 0);

                canvasRef.toBlob((blob) => {
                    if (blob) {
                        imageFile = new File([blob], "camera-capture.jpg", { type: "image/jpeg" });
                        stopCamera();
                    }
                }, "image/jpeg");
            }
        }
    }

    function stopCamera() {
        if (videoRef && videoRef.srcObject) {
            const stream = videoRef.srcObject as MediaStream;
            stream.getTracks().forEach((track) => track.stop());
        }
        showCamera = false;
    }

    async function saveEntity() {
        if (!name.trim()) {
            showError("이름을 입력해주세요");
            return;
        }

        setLoading(true, isAdd ? "엔티티 추가 중..." : "엔티티 수정 중...");

        try {
            const result = await api.multimodalEdit({
                operation: isAdd ? "add" : "edit",
                entity_set_name: $projectState.entity_set_name,
                work_dir: $projectState.work_dir,
                index: index ?? undefined,
                type_: type as EntityType,
                name,
                description,
                extra_prompt: extraPrompt,
                text_model: textModel,
                image_model: imageModel,
                image_style: imageStyle,
                image_quality: imageQuality,
                image_size: imageSize,
                image: imageFile ?? undefined,
            });

            entityList.set(result.entity_list);
            showSuccess(isAdd ? "엔티티가 추가되었습니다" : "엔티티가 수정되었습니다");
            onclose();
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : "엔티티 처리 중 오류가 발생했습니다";
            showError(errorMessage);
        } finally {
            setLoading(false);
        }
    }
</script>

<div
    class="fixed inset-0 flex items-center justify-center p-8"
    style="position: fixed !important; top: 0 !important; left: 0 !important; right: 0 !important; bottom: 0 !important; z-index: 10000 !important; background: rgba(0,0,0,0.5) !important;"
    onclick={onclose}
>
    <!-- Modal Content -->
    <div
        class="relative w-full mx-8 shadow-2xl"
        onclick={(e) => e.stopPropagation()}
        style="background: white !important; border-radius: 8px !important; border: 1px solid #e5e7eb !important; max-width: 1280px !important; max-height: 90vh !important; overflow-y: auto !important; padding: 32px !important; display: block !important;"
    >
        <div class="flex justify-between items-center mb-6">
            <h2 class="text-2xl font-bold">
                {isAdd ? "엔티티 추가" : "엔티티 수정"}
            </h2>
            <button class="btn btn-sm btn-circle btn-ghost" onclick={onclose}>
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
        </div>

        <div class="space-y-4">
            <!-- Type -->
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2"> 타입 </label>
                <select bind:value={type} disabled={!isAdd} class="select select-bordered w-full {!isAdd ? 'select-disabled' : ''}">
                    <option value="character">인물</option>
                    <option value="location">배경</option>
                    <option value="object">사물</option>
                </select>
            </div>

            <!-- Name -->
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2"> 이름 </label>
                <input type="text" bind:value={name} class="input input-bordered w-full" placeholder="이름을 입력하세요" style="box-sizing: border-box !important;" />
            </div>

            <!-- Description -->
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2"> 설명 </label>
                <textarea bind:value={description} rows="3" class="textarea textarea-bordered w-full" placeholder="설명을 입력하세요" style="box-sizing: border-box !important;"></textarea>
            </div>

            <!-- Extra Prompt -->
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2"> 추가 프롬프트 (선택사항) </label>
                <input type="text" bind:value={extraPrompt} placeholder="추가 지시사항을 입력하세요" class="input input-bordered w-full" style="box-sizing: border-box !important;" />
            </div>

            <!-- Image Upload -->
            <div class="form-control">
                <label class="label">
                    <span class="label-text">📷 이미지 업로드 (선택사항)</span>
                </label>
                <div class="flex gap-2">
                    <input type="file" accept="image/*" bind:this={fileInput} onchange={handleFileSelect} class="hidden" />
                    <button onclick={() => fileInput.click()} class="btn btn-outline"> 파일 선택 </button>
                    <button onclick={startCamera} class="btn btn-outline"> 카메라 촬영 </button>
                    {#if imageFile}
                        <div class="badge badge-success gap-2">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                            </svg>
                            {imageFile.name}
                        </div>
                    {/if}
                </div>
            </div>

            <!-- Camera View -->
            {#if showCamera}
                <div class="card bg-base-200 p-4">
                    <video bind:this={videoRef} autoplay class="w-full rounded-lg"></video>
                    <canvas bind:this={canvasRef} class="hidden"></canvas>
                    <div class="flex gap-2 mt-4 justify-center">
                        <button onclick={capturePhoto} class="btn btn-primary"> 촬영 </button>
                        <button onclick={stopCamera} class="btn btn-outline"> 취소 </button>
                    </div>
                </div>
            {/if}

            <!-- Model Settings -->
            <div class="divider"></div>
            <div>
                <h3 class="text-lg font-semibold mb-4">🤖 AI 모델 설정</h3>

                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">텍스트 모델</label>
                        <select bind:value={textModel} class="select select-bordered w-full">
                            {#each textModels as model}
                                <option value={model}>{model}</option>
                            {/each}
                        </select>
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">이미지 모델</label>
                        <select bind:value={imageModel} class="select select-bordered w-full">
                            {#each imageModels as model}
                                <option value={model}>{model}</option>
                            {/each}
                        </select>
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">화풍</label>
                        <select bind:value={imageStyle} class="select select-bordered w-full">
                            {#each imageStyles as style}
                                <option value={style}>{style}</option>
                            {/each}
                        </select>
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">품질</label>
                        <select bind:value={imageQuality} class="select select-bordered w-full">
                            {#each imageQualities as quality}
                                <option value={quality}>{quality}</option>
                            {/each}
                        </select>
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">크기</label>
                        <select bind:value={imageSize} class="select select-bordered w-full">
                            {#each imageSizes as size}
                                <option value={size}>{size}</option>
                            {/each}
                        </select>
                    </div>
                </div>
            </div>
        </div>

        <!-- Action Buttons -->
        <div class="modal-action">
            <button onclick={onclose} class="btn btn-outline"> 취소 </button>
            <button onclick={saveEntity} class="btn btn-primary"> 저장 </button>
        </div>
    </div>
</div>
