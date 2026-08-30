import { Component, input, computed } from '@angular/core';
import { CommonModule, DecimalPipe } from '@angular/common';
import { ModelMeta, ModelResult, PredictionItem } from '../../services/inference.service';

export interface ColumnData {
  meta: ModelMeta;
  result: ModelResult | null;
  loading: boolean;
  error: string | null;
}

@Component({
  selector: 'app-model-column',
  standalone: true,
  imports: [CommonModule, DecimalPipe],
  template: `
    <div class="column" [style.--model-color]="color()">
      <!-- Header -->
      <div class="col-header">
        <span class="color-dot"></span>
        <div class="col-meta">
          <span class="col-label">{{ data().meta.label }}</span>
          @if (data().result) {
            <span class="col-latency mono">{{ data().result!.latency_ms }}ms</span>
          }
        </div>
      </div>

      <!-- Hierarchy path (UX-004: above predictions) -->
      <div class="hierarchy">
        <span class="h-node" [class.h-active]="hasHead('product_family')">PF</span>
        <span class="h-arrow">→</span>
        <span class="h-node" [class.h-active]="hasHead('technology')">TECH</span>
        <span class="h-arrow">→</span>
        <span class="h-node" [class.h-active]="hasHead('brand')">BRAND</span>
        <span class="h-arrow">→</span>
        <span class="h-node" [class.h-active]="hasHead('toolname')">TOOLNAME</span>
      </div>

      <!-- Loading -->
      @if (data().loading) {
        <div class="skeleton-wrap">
          <div class="skeleton"></div>
          <div class="skeleton short"></div>
          <div class="skeleton"></div>
          <div class="skeleton short"></div>
        </div>
      }

      <!-- Error (UX-003) -->
      @if (data().error && !data().loading) {
        <div class="col-error">
          <span class="error-msg">This model didn't respond — try again</span>
          <button class="retry-btn" (click)="onRetry()">Retry</button>
        </div>
      }

      <!-- Results -->
      @if (data().result && !data().loading && !data().error) {
        @for (head of heads(); track head.key) {
          @if (head.preds.length) {
            <div class="head-block">
              <div class="head-label">{{ head.label }}</div>
              @for (pred of head.preds; track pred.label; let i = $index) {
                <div class="pred-row" [class.top]="i === 0">
                  <div class="pred-label" [title]="pred.label">{{ pred.label }}</div>
                  <div class="pred-right">
                    <div class="score-bar-wrap">
                      <div class="score-bar" [style.width.%]="pred.score * 100"></div>
                    </div>
                    <span class="score mono">{{ pred.score | number:'1.3-3' }}</span>
                    @if (i === 0 && bestDelta(head.key) !== null) {
                      <span class="delta" [class.delta-behind]="bestDelta(head.key)! < 0">
                        {{ bestDelta(head.key)! > 0 ? '▲' : '▼' }}
                        {{ (bestDelta(head.key)! | number:'1.3-3')?.replace('-','') }}
                      </span>
                    }
                  </div>
                </div>
              }
            </div>
          }
        }
      }
    </div>
  `,
  styleUrl: './model-column.scss'
})
export class ModelColumnComponent {
  data = input.required<ColumnData>();
  allResults = input<Record<string, ModelResult>>({});

  color = computed(() => `var(--${this.data().meta.color})`);

  heads = computed(() => {
    const r = this.data().result;
    if (!r) return [];
    return [
      { key: 'product_family', label: 'Product Family', preds: r.product_family },
      { key: 'technology',     label: 'Technology',     preds: r.technology },
      { key: 'brand',          label: 'Brand',          preds: r.brand },
      { key: 'toolname',       label: 'Tool Name',      preds: r.toolname },
    ];
  });

  hasHead(key: string): boolean {
    const r = this.data().result;
    if (!r) return false;
    return (r as any)[key]?.length > 0;
  }

  // UX-002: delta = this model's top-1 score minus the best top-1 across all selected models
  bestDelta(headKey: string): number | null {
    const r = this.data().result;
    if (!r) return null;
    const myScore = (r as any)[headKey]?.[0]?.score;
    if (myScore == null) return null;

    const allScores = Object.values(this.allResults())
      .map(res => (res as any)[headKey]?.[0]?.score)
      .filter((s): s is number => s != null);

    if (allScores.length < 2) return null;
    const best = Math.max(...allScores);
    const delta = myScore - best;
    return Math.abs(delta) < 0.0005 ? null : parseFloat(delta.toFixed(3));
  }

  onRetry() {
    // Retry is handled at parent level via event — column just signals intent
    window.dispatchEvent(new CustomEvent('model-delta:retry'));
  }
}
