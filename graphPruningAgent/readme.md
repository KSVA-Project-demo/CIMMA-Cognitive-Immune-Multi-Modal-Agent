
# Multi-Modal Knowledge Graph → Exam Concept Pipeline

This repository provides a compact pipeline that converts images (plus optional text) into a structured knowledge graph, prunes it with a hybrid approach, analyzes and visualizes results, and finally maps the pruned graph to likely exam knowledge points.


## At a glance


Recent updates:


## Quickstart (PowerShell)

1. Set environment variables for the session (API key and optional proxy):

```powershell
$env:GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
$env:HTTP_PROXY = 'http://127.0.0.1:7890'   # optional
$env:HTTPS_PROXY = 'http://127.0.0.1:7890'  # optional
```

2. Install dependencies if needed:

```powershell
pip install -r requirements.txt
```

3. Run the pipeline (interactive local mode saves outputs and opens viewer windows):

```powershell
python .\workflow.py
```

Tip: the pipeline will create a folder like `Output_20260203_115747` containing all artifacts.


## Files & Useful commands


```powershell
python .\match_kb.py --kg Output_XXXX\3_KG_P.json --kb exam_kb.json --out Output_XXXX
```



## match_kb: what to expect


If you change KB text or the embedding model, re-run the KB embedding step — `match_kb` will auto-generate and cache missing embeddings on first run.


## Embedding & cost note



## Troubleshooting & tips



## Next improvements (suggested)

1. Replace template KB titles with real syllabus-aligned topic names & descriptions to improve match quality.
2. Tune `match_kb` weights (alpha/beta/gamma in `match_kb.py`) and thresholds with a small validation set.
3. If KB grows, use FAISS (or similar) for fast vector search.


If you want, I can now: build a FAISS index from the cached embeddings, refine KB text contents, or run a small evaluation that prints top-5 evidence per run. Tell me which and I will proceed.


      * Ensure your API Key is active and has access to `gemini-1.5-flash` and `text-embedding-004`.

3.  **Matplotlib Chinese Characters Display as Boxes (□□)**:

      * The scripts try to use standard fonts (`SimHei`, `Arial Unicode MS`). If you still see boxes, you may need to install a CJK font on your system or modify `plt.rcParams['font.sans-serif']`.

4.  **Library deprecation & linter noise**:

      * The project currently uses the `google.generativeai` client which is deprecated. You may see a FutureWarning at runtime; consider migrating to `google.genai` in the future.
      * When running `flake8` you may see a lot of irrelevant warnings coming from local environment folders (for example `.conda`). To reduce noise, add a `.flake8` file in the project root with exclusions, for example:

```ini
[flake8]
exclude = .venv,.env,__pycache__,.git,.conda,Output_*
max-line-length = 120
```

      * After adding the above, re-run `flake8` to get focused lint results on the project files.


## 📄 License

This project is provided for educational and research purposes.
## Multi-Modal Knowledge Graph → Exam Concept Pipeline

This repository implements a compact pipeline that converts visual inputs (images) and optional textual/audio context into a structured knowledge graph (KG), prunes the KG using a hybrid semantic approach, analyzes and visualizes the result, and maps the pruned KG to candidate exam knowledge points.

This README was updated to describe the Phase‑0 multimodal additions: a lightweight `audio_api` scaffold and a non-invasive workflow change that appends ASR transcripts to the LLM summarizer when local audio is available.

## Key features

- Inputs: image (e.g., `test.png`), optional descriptive text, optional short audio file (e.g., `test.wav`).
- Pipeline steps: image + text (and optionally audio) summarization → KG extraction → semantic pruning → analysis & visualization → SVG scene generation → KB matching.
- Outputs: an `Output_YYYYMMDD_HHMMSS` folder containing intermediate JSONs, visualizations, Excel analysis, and the final `6_core_concepts.json` (selected KB concepts with evidence).

## What changed in this update

- Added `graphPruningAgent/audio_api.py` (Phase‑0 scaffold):
  - `transcribe(audio_path)` — tries local Whisper (if installed), returns a transcript or a clear fallback/note.
  - `summarize_transcript(transcript)` — a tiny truncation helper to limit prompt size.
- Updated `graphPruningAgent/workflow.py` to optionally detect a local `test.wav` and append a short audio transcript to the user prompt before calling the LLM summarizer (`api.summarize_image_and_text`). This keeps the integration lightweight and non-blocking when ASR or credentials are not available.

These changes are intentionally minimal so the pipeline continues to work even without ASR or API keys.

## Quickstart (PowerShell)

1. Set environment variables for the session (API key and optional proxy):

```powershell
$env:GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
$env:HTTP_PROXY = 'http://127.0.0.1:7890'   # optional
$env:HTTPS_PROXY = 'http://127.0.0.1:7890'  # optional
```

2. Install dependencies (if a `requirements.txt` is present):

```powershell
pip install -r requirements.txt
```

3. Prepare inputs (place files in the repository folder):

- `test.png` — example image used by the workflow.
- `test.wav` — optional local audio that will be transcribed and appended to the prompt if present.

4. Run the pipeline locally:

```powershell
python .\workflow.py
```

The run will create a timestamped `Output_...` directory with JSONs, images, Excel reports and `6_core_concepts.json`.

## How audio is handled (Phase 0)

- The `audio_api.transcribe` function attempts to use the `whisper` Python package if it is installed and available locally. If Whisper is not present or fails, `transcribe` returns an informative `note` and an empty transcript so the workflow continues without blocking.
- Any non-empty transcript is truncated by `summarize_transcript()` and appended to the LLM prompt passed to `api.summarize_image_and_text`.
- This pattern avoids immediate reliance on cloud ASR or credentials while enabling multimodal prompts for local testing.

## Files of interest

- `workflow.py` — orchestrates the full pipeline and now performs optional local audio transcription and prompt augmentation.
- `api.py` — wraps the image+text summarization call to the LLM (Gemini client in the repo).
- `generateKG.py` — contains `extract_knowledge_graph()` and visualization helpers.
- `pruningKG.py` — semantic KG pruning logic backed by the LLM.
- `match_kb.py` — embedding-based KB matching and ranking logic that produces `6_core_concepts.json`.
- `audio_api.py` — new Phase‑0 ASR scaffold.

## Notes, warnings and troubleshooting

- API keys: if `GOOGLE_API_KEY` is not set you will see warnings when modules try to call external LLM/embedding services. Set the environment variable to enable full functionality.
- Whisper: to enable local audio transcription install `openai-whisper` (or your preferred ASR). Without it the workflow will still run but skip audio content.
- Deprecation: the repo currently uses `google.generativeai` which emits a FutureWarning. Consider migrating to `google.genai` for future compatibility.



## License

This project is provided for educational and research purposes.