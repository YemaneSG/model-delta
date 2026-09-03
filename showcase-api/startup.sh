#!/bin/bash
set -e

MODEL_ROOT="${MODEL_ROOT:-/app/models}"
HF_REPO="YemFelix/asset-taxonomy-proxy-models"

echo "=== model-delta startup ==="
echo "MODEL_ROOT: $MODEL_ROOT"
echo "HF_REPO: $HF_REPO"

mkdir -p "$MODEL_ROOT"

# Download TF-IDF proxy
if [ ! -f "$MODEL_ROOT/synth_v1/clf_pf.joblib" ]; then
    echo "Downloading tfidf-synth from HuggingFace..."
    python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='$HF_REPO',
    allow_patterns=['tfidf-synth/**'],
    local_dir='$MODEL_ROOT',
    local_dir_use_symlinks=False,
)
"
    # HF downloads to tfidf-synth/, rename to synth_v1/
    mv "$MODEL_ROOT/tfidf-synth" "$MODEL_ROOT/synth_v1" 2>/dev/null || true
    echo "TF-IDF done."
fi

# Download ModernBERT proxy heads
for head in pf tech brand; do
    hf_dir="modernbert-${head}"
    local_dir="$MODEL_ROOT/slm/models/synthesized/${head}"
    if [ ! -d "$local_dir" ]; then
        echo "Downloading $hf_dir from HuggingFace..."
        python -c "
from huggingface_hub import snapshot_download
import os, shutil
snapshot_download(
    repo_id='$HF_REPO',
    allow_patterns=['${hf_dir}/**'],
    local_dir='/tmp/hf_${head}',
    local_dir_use_symlinks=False,
)
os.makedirs('$(dirname $local_dir)', exist_ok=True)
shutil.move('/tmp/hf_${head}/${hf_dir}', '$local_dir')
"
        echo "$head done."
    fi
done

echo "All models ready. Starting server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
