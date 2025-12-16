import { writable, derived } from 'svelte/store';
import type { 
  ProjectState, 
  EntityTuple, 
  Scene, 
  Cut, 
  ApiLogEntry,
  TextModel,
  ImageModel,
  VideoModel,
  ImageStyle,
  ImageQuality,
  ImageSize
} from './types';

// Project State Store
function createProjectStore() {
  const defaultState: ProjectState = {
    work_dir: '',
    entity_set_name: '',
    default_text_model: 'gpt-4.1',
    default_image_model: 'gpt-image-1',
    default_video_model: 'veo-3.1-fast-generate-preview',
    default_image_style: 'realistic',
    default_image_quality: 'low',
    default_image_size: '1536x1024'
  };

  const storedState = typeof window !== 'undefined' 
    ? localStorage.getItem('projectState') 
    : null;
  
  const initialState = storedState 
    ? { ...defaultState, ...JSON.parse(storedState) }
    : defaultState;

  const { subscribe, set, update } = writable<ProjectState>(initialState);

  return {
    subscribe,
    set: (value: ProjectState) => {
      if (typeof window !== 'undefined') {
        localStorage.setItem('projectState', JSON.stringify(value));
      }
      set(value);
    },
    update: (updater: (value: ProjectState) => ProjectState) => {
      update((value) => {
        const newValue = updater(value);
        if (typeof window !== 'undefined') {
          localStorage.setItem('projectState', JSON.stringify(newValue));
        }
        return newValue;
      });
    },
    reset: () => {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('projectState');
      }
      set(defaultState);
    }
  };
}

export const projectState = createProjectStore();

// Entity List Store
export const entityList = writable<EntityTuple[]>([]);

// Scenes Store
export const scenes = writable<Scene[]>([]);

// Cuts Store (2D array: cuts grouped by scene)
export const cuts = writable<Cut[][]>([]);

// Cut Images Store
export const cutImages = writable<Map<string, string>>(new Map());

// Cut Videos Store
export const cutVideos = writable<Map<string, string>>(new Map());

// Final Video Path Store - no localStorage as it depends on project
export const finalVideoPath = writable<string>('');

// Loading State Store
export const isLoading = writable<boolean>(false);
export const loadingMessage = writable<string>('');

// API Logs Store
function createApiLogsStore() {
  const { subscribe, update } = writable<ApiLogEntry[]>([]);

  return {
    subscribe,
    addLog: (entry: ApiLogEntry) => {
      update(logs => [entry, ...logs].slice(0, 100)); // Keep last 100 logs
    },
    updateLog: (id: string, updates: Partial<ApiLogEntry>) => {
      update(logs => 
        logs.map(log => 
          log.id === id ? { ...log, ...updates } : log
        )
      );
    },
    clear: () => {
      update(() => []);
    }
  };
}

export const apiLogs = createApiLogsStore();

// Derived store for API logs visibility
export const showApiLogs = writable<boolean>(false);

// Selected cuts for generation
export const selectedCuts = writable<Set<string>>(new Set());

// Current step in the workflow
export const currentStep = writable<number>(0);

// Error message store
export const errorMessage = writable<string>('');

// Success message store
export const successMessage = writable<string>('');

// Helper functions
export function setLoading(loading: boolean, message: string = '') {
  isLoading.set(loading);
  loadingMessage.set(message);
}

export function showError(message: string) {
  errorMessage.set(message);
  setTimeout(() => errorMessage.set(''), 5000);
}

export function showSuccess(message: string) {
  successMessage.set(message);
  setTimeout(() => successMessage.set(''), 3000);
}

// Utility function to generate cut ID
export function getCutId(sceneNum: number, cutNum: number): string {
  return `S${sceneNum.toString().padStart(4, '0')}-C${cutNum.toString().padStart(4, '0')}`;
}