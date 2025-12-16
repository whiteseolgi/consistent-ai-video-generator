// Entity Types
export type EntityType = "character" | "location" | "object";
export type EntityTuple = [EntityType, string, string, string | null]; // [type, name, description, image_path]

export interface Entity {
    type: EntityType;
    name: string;
    description: string;
    image_path?: string | null;
}

// Scene and Cut Types
export interface Scene {
    scene_number: number;
    description: string;
    [key: string]: any;
}

export interface Cut {
    cut_id: number;
    description: string;
    entities?: string[];
    [key: string]: any;
}

// AI Model Types
export type TextModel = "gpt-4.1" | "gpt-4o" | "gpt-5" | "gpt-5.1";
export type ImageModel = "gpt-image-1" | "gemini-2.5-flash-imag(Nano Banana)" | "gemini-3-pro-image-preview(Nano Banana Pro)";
export type VideoModel = "runway" | "sora2" | "veo-3.0-fast-generate-001" | "veo-3.0-generate-001" | "veo-3.1-fast-generate-preview" | "veo-3.1-generate-preview";
export type ImageStyle = "realistic" | "illustration" | "anime" | "watercolor" | "oil_painting" | "comic" | "storybook" | "sketch" | "pixel_art" | "lowpoly";
export type ImageQuality = "low" | "medium" | "high";
export type ImageSize = "1024x1024" | "1536x1024" | "2048x2048";

// API Request Types
export interface SynopsisAnalyzeRequest {
    entity_set_name?: string;
    work_dir?: string;
    synopsis_text?: string;
    synopsis_text_path?: string;
    synopsis_text_file?: File;
    analyzer_save_dir?: string;
    text_model: TextModel;
}

export interface CreateEntitiesRequest {
    entity_set_name?: string;
    work_dir?: string;
    entity_dict_draft_list?: any[];
    entity_draft_json_path?: string;
    entity_draft_json_file?: File;
    reference_image_dir?: string;
    entity_list_output_path?: string;
    image_model: ImageModel;
    image_style: ImageStyle;
    image_quality: ImageQuality;
    image_size: ImageSize;
}

export interface MultimodalEditRequest {
    operation: "edit" | "add";
    entity_set_name?: string;
    work_dir?: string;
    entity_list_path?: string;
    reference_image_dir?: string;
    index?: number;
    type_?: EntityType;
    name?: string;
    description?: string;
    extra_prompt?: string;
    text_model: TextModel;
    image_model: ImageModel;
    image_style: ImageStyle;
    image_quality: ImageQuality;
    image_size: ImageSize;
    image?: File;
}

export interface GenerateScenesRequest {
    entity_set_name?: string;
    work_dir?: string;
    story_text?: string;
    story_text_path?: string;
    story_text_file?: File;
    output_scene_txt_path?: string;
    text_model: TextModel;
}

export interface GenerateCutsRequest {
    entity_set_name?: string;
    work_dir?: string;
    scenes?: Scene[];
    scenes_txt_path?: string;
    scenes_txt_file?: File;
    entity_list_path?: string;
    entity_list_file?: File;
    story_text?: string;
    story_text_path?: string;
    story_text_file?: File;
    cuts_output_path?: string;
    text_model: TextModel;
}

export interface GenerateCutImagesRequest {
    entity_set_name?: string;
    work_dir?: string;
    entity_list_path?: string;
    entity_list_file?: File;
    cut_list_path?: string;
    cut_list_file?: File;
    cut_image_output_dir?: string;
    entity_image_dir?: string;
    image_model: ImageModel;
    image_style: ImageStyle;
    image_quality: ImageQuality;
    image_size: ImageSize;
    scene_num?: number;
    cut_num?: number;
    selected_cuts?: Array<{ scene_num: number; cut_num: number }>;
}

export interface GenerateCutVideosRequest {
    entity_set_name?: string;
    work_dir?: string;
    cut_image_dir?: string;
    cut_image_paths?: string[] | any; // Array that will be JSON stringified
    cut_list_path?: string;
    cut_list_file?: File;
    video_output_dir?: string;
    video_model: VideoModel;
    scene_num?: number;
    cut_num?: number;
}

export interface ConcatVideosRequest {
    entity_set_name?: string;
    work_dir?: string;
    video_clip_paths?: string[];
    video_output_dir?: string;
    clip_list_path?: string;
    final_output_path?: string;
}

// API Response Types
export interface SynopsisAnalyzeResponse {
    entity_dict_draft_list: any[];
    saved_txt_path: string;
    saved_json_path: string;
}

export interface CreateEntitiesResponse {
    entity_list: EntityTuple[];
    entity_list_output_path: string;
}

export interface MultimodalEditResponse {
    entity_list: EntityTuple[];
    entity_list_path: string;
}

export interface GenerateScenesResponse {
    scenes: Scene[];
    output_scene_txt_path?: string;
}

export interface GenerateCutsResponse {
    cut_list: Cut[][];
    cuts_output_path: string;
}

export interface GenerateCutImagesResponse {
    cut_image_paths: string[];
}

export interface GenerateCutVideosResponse {
    video_clip_paths: string[];
}

export interface ConcatVideosResponse {
    final_output_path: string;
}

// Project State
export interface ProjectState {
    work_dir: string;
    entity_set_name: string;
    default_text_model: TextModel;
    default_image_model: ImageModel;
    default_video_model: VideoModel;
    default_image_style: ImageStyle;
    default_image_quality: ImageQuality;
    default_image_size: ImageSize;
}

// API Log Entry
export interface ApiLogEntry {
    id: string;
    timestamp: Date;
    endpoint: string;
    method: string;
    status: "pending" | "success" | "error";
    message?: string;
    error?: string;
}
