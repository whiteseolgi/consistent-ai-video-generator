import { PUBLIC_API_URL } from '$env/static/public';
import type {
  SynopsisAnalyzeRequest,
  SynopsisAnalyzeResponse,
  CreateEntitiesRequest,
  CreateEntitiesResponse,
  MultimodalEditRequest,
  MultimodalEditResponse,
  GenerateScenesRequest,
  GenerateScenesResponse,
  GenerateCutsRequest,
  GenerateCutsResponse,
  GenerateCutImagesRequest,
  GenerateCutImagesResponse,
  GenerateCutVideosRequest,
  GenerateCutVideosResponse,
  ConcatVideosRequest,
  ConcatVideosResponse,
  ApiLogEntry,
  EntityTuple
} from './types';
import { apiLogs } from './stores';

class ApiClient {
  private baseUrl: string;
  private dynamicBaseUrl: string | null = null;
  private initPromise: Promise<void> | null = null;

  constructor() {
    this.baseUrl = PUBLIC_API_URL || 'http://localhost:8000';
    this.initPromise = this.initializeDynamicUrl();
  }

  private async initializeDynamicUrl(): Promise<void> {
    try {
      // 먼저 현재 호스트의 IP를 시도
      const currentHost = window.location.hostname;
      if (currentHost !== 'localhost' && currentHost !== '127.0.0.1') {
        const testUrl = `http://${currentHost}:8000`;
        const response = await fetch(`${testUrl}/health`, { 
          method: 'GET',
          signal: AbortSignal.timeout(3000)
        });
        if (response.ok) {
          this.dynamicBaseUrl = testUrl;
          return;
        }
      }

      // 다음으로 서버 정보 API로 동적 IP 감지 시도
      const serverInfoUrl = `${this.baseUrl}/server-info`;
      const response = await fetch(serverInfoUrl, {
        method: 'GET',
        signal: AbortSignal.timeout(3000)
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.api_url && data.api_url !== this.baseUrl) {
          // 동적 감지된 URL이 작동하는지 테스트
          const testResponse = await fetch(`${data.api_url}/health`, {
            method: 'GET',
            signal: AbortSignal.timeout(3000)
          });
          if (testResponse.ok) {
            this.dynamicBaseUrl = data.api_url;
          }
        }
      }
    } catch (error) {
      console.log('Dynamic IP detection failed, using default URL:', error instanceof Error ? error.message : String(error));
    }
  }

  private async ensureInitialized(): Promise<void> {
    if (this.initPromise) {
      await this.initPromise;
    }
  }

  private getBaseUrl(): string {
    return this.dynamicBaseUrl || this.baseUrl;
  }

  // 동기적 URL 접근을 위한 메서드 (초기화 완료 전에도 사용 가능)
  private getBaseUrlSync(): string {
    return this.dynamicBaseUrl || this.baseUrl;
  }

  private generateId(): string {
    // Use crypto.randomUUID if available, otherwise fallback to custom implementation
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
      return crypto.randomUUID();
    }
    
    // Fallback for browsers/environments that don't support crypto.randomUUID
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  private logRequest(endpoint: string, method: string): string {
    const id = this.generateId();
    const entry: ApiLogEntry = {
      id,
      timestamp: new Date(),
      endpoint,
      method,
      status: 'pending'
    };
    apiLogs.addLog(entry);
    return id;
  }

  private updateLog(id: string, status: 'success' | 'error', message?: string, error?: string) {
    apiLogs.updateLog(id, { status, message, error });
  }

  private async fetchWithRetry(url: string, options: RequestInit, retries = 2): Promise<Response> {
    let lastError: Error | null = null;
    
    for (let i = 0; i <= retries; i++) {
      try {
        const response = await fetch(url, options);
        if (response.ok) return response;
        
        // Don't retry on client errors (4xx)
        if (response.status >= 400 && response.status < 500) {
          const errorText = await response.text();
          throw new Error(`요청 실패: ${response.status} - ${errorText}`);
        }
        
        // Retry on server errors (5xx)
        if (response.status >= 500 && i < retries) {
          await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
          continue;
        }
        
        throw new Error(`서버 오류: ${response.status}`);
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));
        if (i < retries && !error.message.includes('요청 실패')) {
          await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
        } else {
          throw error;
        }
      }
    }
    
    throw lastError || new Error('요청 실패');
  }

  private createFormData(data: any): FormData {
    const formData = new FormData();
    
    for (const [key, value] of Object.entries(data)) {
      if (value === undefined || value === null) continue;
      
      if (value instanceof File) {
        formData.append(key, value);
      } else if (Array.isArray(value)) {
        formData.append(key, JSON.stringify(value));
      } else if (typeof value === 'object') {
        formData.append(key, JSON.stringify(value));
      } else {
        formData.append(key, String(value));
      }
    }
    
    return formData;
  }

  async analyzeSynopsis(request: SynopsisAnalyzeRequest): Promise<SynopsisAnalyzeResponse> {
    const logId = this.logRequest('/analyze-synopsis', 'POST');
    
    try {
      const formData = this.createFormData(request);
      const response = await this.fetchWithRetry(`${this.getBaseUrl()}/analyze-synopsis`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      this.updateLog(logId, 'success', '시놉시스 분석 완료');
      return data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류';
      this.updateLog(logId, 'error', undefined, errorMessage);
      throw new Error(`시놉시스 분석 실패: ${errorMessage}`);
    }
  }

  async createEntities(request: CreateEntitiesRequest): Promise<CreateEntitiesResponse> {
    const logId = this.logRequest('/create-entities', 'POST');
    
    try {
      const formData = this.createFormData(request);
      const response = await fetch(`${this.getBaseUrl()}/create-entities`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      this.updateLog(logId, 'success', 'Entities created successfully');
      return data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.updateLog(logId, 'error', undefined, errorMessage);
      throw error;
    }
  }

  async multimodalEdit(request: MultimodalEditRequest): Promise<MultimodalEditResponse> {
    const logId = this.logRequest('/multimodal/edit-or-add', 'POST');
    
    try {
      const formData = this.createFormData(request);
      const response = await fetch(`${this.getBaseUrl()}/multimodal/edit-or-add`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      this.updateLog(logId, 'success', `Entity ${request.operation === 'edit' ? 'edited' : 'added'} successfully`);
      return data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.updateLog(logId, 'error', undefined, errorMessage);
      throw error;
    }
  }

  async generateScenes(request: GenerateScenesRequest): Promise<GenerateScenesResponse> {
    const logId = this.logRequest('/generate-scenes', 'POST');
    
    try {
      const formData = this.createFormData(request);
      const response = await fetch(`${this.getBaseUrl()}/generate-scenes`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      this.updateLog(logId, 'success', 'Scenes generated successfully');
      return data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.updateLog(logId, 'error', undefined, errorMessage);
      throw error;
    }
  }

  async generateCuts(request: GenerateCutsRequest): Promise<GenerateCutsResponse> {
    const logId = this.logRequest('/generate-cuts', 'POST');
    
    try {
      const formData = this.createFormData(request);
      const response = await fetch(`${this.getBaseUrl()}/generate-cuts`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      this.updateLog(logId, 'success', 'Cuts generated successfully');
      return data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.updateLog(logId, 'error', undefined, errorMessage);
      throw error;
    }
  }

  async generateCutImages(request: GenerateCutImagesRequest): Promise<GenerateCutImagesResponse> {
    const logId = this.logRequest('/generate-cut-images', 'POST');
    
    try {
      const formData = this.createFormData(request);
      const response = await fetch(`${this.getBaseUrl()}/generate-cut-images`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      this.updateLog(logId, 'success', 'Cut images generated successfully');
      return data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.updateLog(logId, 'error', undefined, errorMessage);
      throw error;
    }
  }

  async generateCutVideos(request: GenerateCutVideosRequest): Promise<GenerateCutVideosResponse> {
    const logId = this.logRequest('/generate-cut-videos', 'POST');
    
    try {
      const formData = this.createFormData(request);
      const response = await fetch(`${this.getBaseUrl()}/generate-cut-videos`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      this.updateLog(logId, 'success', 'Cut videos generated successfully');
      return data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.updateLog(logId, 'error', undefined, errorMessage);
      throw error;
    }
  }

  async concatVideos(request: ConcatVideosRequest): Promise<ConcatVideosResponse> {
    const logId = this.logRequest('/concat-videos', 'POST');
    
    try {
      const formData = this.createFormData(request);
      const response = await fetch(`${this.getBaseUrl()}/concat-videos`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      this.updateLog(logId, 'success', 'Videos concatenated successfully');
      return data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.updateLog(logId, 'error', undefined, errorMessage);
      throw error;
    }
  }

  // New method to load existing entity list
  async loadEntityList(workDir: string, entitySetName: string): Promise<EntityTuple[]> {
    const logId = this.logRequest('/load-entity-list', 'GET');
    
    try {
      const response = await fetch(`${this.getBaseUrl()}/load-entity-list?work_dir=${encodeURIComponent(workDir)}&entity_set_name=${encodeURIComponent(entitySetName)}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          this.updateLog(logId, 'success', 'No entity list found');
          return [];
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      this.updateLog(logId, 'success', 'Entity list loaded successfully');
      return data.entity_list || [];
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.updateLog(logId, 'error', undefined, errorMessage);
      return [];
    }
  }

  // Load existing scenes
  async loadScenes(workDir: string, entitySetName: string): Promise<any[]> {
    const logId = this.logRequest('/load-scenes', 'GET');
    
    try {
      const response = await fetch(`${this.getBaseUrl()}/load-scenes?work_dir=${encodeURIComponent(workDir)}&entity_set_name=${encodeURIComponent(entitySetName)}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          this.updateLog(logId, 'success', 'No scenes found');
          return [];
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      this.updateLog(logId, 'success', 'Scenes loaded successfully');
      return data.scenes || [];
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.updateLog(logId, 'error', undefined, errorMessage);
      return [];
    }
  }

  // Load existing cuts
  async loadCuts(workDir: string, entitySetName: string): Promise<any[][]> {
    const logId = this.logRequest('/load-cuts', 'GET');
    
    try {
      const response = await fetch(`${this.getBaseUrl()}/load-cuts?work_dir=${encodeURIComponent(workDir)}&entity_set_name=${encodeURIComponent(entitySetName)}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          this.updateLog(logId, 'success', 'No cuts found');
          return [];
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      this.updateLog(logId, 'success', 'Cuts loaded successfully');
      return data.cuts || [];
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.updateLog(logId, 'error', undefined, errorMessage);
      return [];
    }
  }

  async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.getBaseUrl()}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }

  // 디버깅용 메서드
  getDebugInfo() {
    return {
      baseUrl: this.baseUrl,
      dynamicBaseUrl: this.dynamicBaseUrl,
      currentUrl: this.getBaseUrl(),
      hostname: window.location.hostname
    };
  }

  // 이미지 URL 생성 (동기적)
  getImageUrl(workDir: string, entitySetName: string, relativePath: string): string {
    const params = new URLSearchParams({
      work_dir: workDir,
      entity_set_name: entitySetName,
      relative_path: relativePath
    });
    const url = `${this.getBaseUrlSync()}/static/image?${params.toString()}`;
    console.log('Generated image URL:', url);
    return url;
  }

  // 비디오 URL 생성 (동기적)
  getVideoUrl(workDir: string, entitySetName: string, relativePath: string): string {
    const params = new URLSearchParams({
      work_dir: workDir,
      entity_set_name: entitySetName,
      relative_path: relativePath
    });
    const url = `${this.getBaseUrlSync()}/static/video?${params.toString()}`;
    console.log('Generated video URL:', url);
    return url;
  }

  // 최종 비디오 URL 생성 (동기적)
  getFinalVideoUrl(workDir: string, entitySetName: string): string {
    const params = new URLSearchParams({
      work_dir: workDir,
      entity_set_name: entitySetName
    });
    const url = `${this.getBaseUrlSync()}/final-video?${params.toString()}`;
    console.log('Generated final video URL:', url);
    return url;
  }

  // 초기화를 기다리고 URL 생성 (비동기적)
  async getImageUrlAsync(workDir: string, entitySetName: string, relativePath: string): Promise<string> {
    await this.ensureInitialized();
    return this.getImageUrl(workDir, entitySetName, relativePath);
  }

  async getVideoUrlAsync(workDir: string, entitySetName: string, relativePath: string): Promise<string> {
    await this.ensureInitialized();
    return this.getVideoUrl(workDir, entitySetName, relativePath);
  }

  async getFinalVideoUrlAsync(workDir: string, entitySetName: string): Promise<string> {
    await this.ensureInitialized();
    return this.getFinalVideoUrl(workDir, entitySetName);
  }

  // Load synopsis text
  async loadSynopsisText(workDir: string, entitySetName: string): Promise<string> {
    try {
      const response = await fetch(`${this.getBaseUrl()}/load-synopsis-text?work_dir=${encodeURIComponent(workDir)}&entity_set_name=${encodeURIComponent(entitySetName)}`);
      if (!response.ok) return '';
      const data = await response.json();
      return data.text || '';
    } catch {
      return '';
    }
  }

  // Load story text
  async loadStoryText(workDir: string, entitySetName: string): Promise<{ text: string; source: string }> {
    try {
      const response = await fetch(`${this.getBaseUrl()}/load-story-text?work_dir=${encodeURIComponent(workDir)}&entity_set_name=${encodeURIComponent(entitySetName)}`);
      if (!response.ok) return { text: '', source: 'none' };
      const data = await response.json();
      return data;
    } catch {
      return { text: '', source: 'none' };
    }
  }

  // List existing projects
  async listProjects(workDir: string): Promise<string[]> {
    try {
      const response = await fetch(`${this.getBaseUrl()}/list-projects?work_dir=${encodeURIComponent(workDir)}`);
      if (!response.ok) return [];
      const data = await response.json();
      return data.projects || [];
    } catch {
      return [];
    }
  }

  // Load cut images
  async loadCutImages(workDir: string, entitySetName: string): Promise<Array<{
    scene_num: number;
    cut_num: number;
    filename: string;
    path: string;
  }>> {
    try {
      const response = await fetch(`${this.getBaseUrl()}/load-cut-images?work_dir=${encodeURIComponent(workDir)}&entity_set_name=${encodeURIComponent(entitySetName)}`);
      if (!response.ok) return [];
      const data = await response.json();
      return data.images || [];
    } catch {
      return [];
    }
  }

  // Load cut videos
  async loadCutVideos(workDir: string, entitySetName: string): Promise<Array<{
    scene_num: number;
    cut_num: number;
    filename: string;
    path: string;
  }>> {
    try {
      const response = await fetch(`${this.getBaseUrl()}/load-cut-videos?work_dir=${encodeURIComponent(workDir)}&entity_set_name=${encodeURIComponent(entitySetName)}`);
      if (!response.ok) return [];
      const data = await response.json();
      return data.videos || [];
    } catch {
      return [];
    }
  }
}

export const api = new ApiClient();