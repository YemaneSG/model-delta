import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ModelMeta {
  id: string;
  label: string;
  color: string;
  metrics: Record<string, number>;
  memory_mb: number;
}

export interface PredictionItem {
  label: string;
  score: number;
}

export interface ModelResult {
  product_family: PredictionItem[];
  technology: PredictionItem[];
  brand: PredictionItem[];
  toolname: PredictionItem[];
  latency_ms: number;
}

export interface PredictResponse {
  results: Record<string, ModelResult>;
  selected_models: string[];
  input: { part_number: string; description: string };
}

const API = 'http://localhost:8000';

@Injectable({ providedIn: 'root' })
export class InferenceService {
  private http = inject(HttpClient);

  getModels(): Observable<ModelMeta[]> {
    return this.http.get<ModelMeta[]>(`${API}/models`);
  }

  predict(modelIds: string[], partNumber: string, description: string): Observable<PredictResponse> {
    return this.http.post<PredictResponse>(`${API}/predict`, {
      model_ids: modelIds,
      part_number: partNumber,
      description,
    });
  }
}
