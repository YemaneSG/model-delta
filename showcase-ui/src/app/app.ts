import { Component, signal, computed, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { InferenceService, ModelMeta, ModelResult, PredictResponse } from './services/inference.service';
import { ModelColumnComponent, ColumnData } from './components/model-column/model-column';

const CANONICAL_PN   = '100390315';
const CANONICAL_DESC = 'FLOW CROSSOVER ASSY';
const DEFAULT_MODELS = ['tfidf-v3', 'modernbert-brand-v1'];
const MAX_MODELS     = 4;

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, ModelColumnComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnInit {
  private svc = inject(InferenceService);

  // State
  models    = signal<ModelMeta[]>([]);
  selected  = signal<Set<string>>(new Set(DEFAULT_MODELS));
  partNum   = signal(CANONICAL_PN);
  desc      = signal(CANONICAL_DESC);
  running   = signal(false);
  results   = signal<Record<string, ModelResult>>({});
  errors    = signal<Record<string, string>>({});
  hasRun    = signal(false);

  // Derived
  selectedList = computed(() => [...this.selected()]);

  columns = computed<ColumnData[]>(() =>
    this.selectedList().map(id => ({
      meta:    this.models().find(m => m.id === id) ?? { id, label: id, color: 'indigo', metrics: {}, memory_mb: 0 },
      result:  this.results()[id] ?? null,
      loading: this.running(),
      error:   this.errors()[id] ?? null,
    }))
  );

  ngOnInit() {
    this.svc.getModels().subscribe(ms => {
      this.models.set(ms);
      // Auto-run with canonical example on load (UX-005)
      this.run();
    });

    window.addEventListener('model-delta:retry', () => this.run());
  }

  toggle(id: string) {
    const s = new Set(this.selected());
    if (s.has(id)) {
      if (s.size > 1) s.delete(id);
    } else {
      if (s.size < MAX_MODELS) s.add(id);
    }
    this.selected.set(s);
  }

  isSelected(id: string) { return this.selected().has(id); }

  canAdd(id: string) { return this.selected().has(id) || this.selected().size < MAX_MODELS; }

  colorVar(color: string) { return `var(--${color})`; }

  run() {
    if (this.running() || !this.partNum().trim() || !this.desc().trim()) return;
    this.running.set(true);
    this.errors.set({});
    this.hasRun.set(true);

    this.svc.predict(this.selectedList(), this.partNum().trim(), this.desc().trim()).subscribe({
      next: (res: PredictResponse) => {
        this.results.set(res.results);
        this.running.set(false);
      },
      error: (err) => {
        // Mark all selected models as errored
        const errs: Record<string, string> = {};
        this.selectedList().forEach(id => errs[id] = err.message ?? 'Request failed');
        this.errors.set(errs);
        this.running.set(false);
      }
    });
  }
}
