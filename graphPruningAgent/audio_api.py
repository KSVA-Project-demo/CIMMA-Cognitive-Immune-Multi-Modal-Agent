"""Audio utilities: ASR transcription and simple audio summarization.

Phase 0 scaffold: try local Whisper if installed, otherwise return a clear placeholder
transcript and instructions. This file is intentionally lightweight and provides
graceful fallback so the pipeline can run in environments without ASR dependencies.
"""
from typing import Dict, Any
import os


def transcribe(audio_path: str, model: str = "small") -> Dict[str, Any]:
    """Transcribe audio to text.

    Returns a dict with keys:
      - transcript: full text
      - segments: optional list of {'start','end','text','confidence'}
      - backend: which backend was used
      - note: optional string with warnings

    This function tries to use `whisper` if available. If not, it returns a
    placeholder transcript and instruction to the user.
    """
    if not os.path.exists(audio_path):
        return {"transcript": "", "segments": [], "backend": None, "note": f"audio file not found: {audio_path}"}

    # Try local Whisper first
    try:
        import whisper
        model_w = whisper.load_model(model)
        result = model_w.transcribe(audio_path)
        # result contains 'text' and 'segments' in recent whisper versions
        transcript = result.get('text', '')
        segments = result.get('segments', []) if isinstance(result, dict) else []
        segs = []
        for s in segments:
            segs.append({
                'start': s.get('start'),
                'end': s.get('end'),
                'text': s.get('text'),
                'confidence': s.get('confidence', None)
            })
        return {"transcript": transcript, "segments": segs, "backend": f"whisper-{model}", "note": None}
    except Exception as e:
        # Whisper not available or failed; fallback
        note = (
            "Whisper transcription not available (exception).\n"
            "Install 'openai-whisper' or provide pre-transcribed text.\n"
            f"Error: {e}"
        )
        return {"transcript": "", "segments": [], "backend": None, "note": note}


def summarize_transcript(transcript: str, max_chars: int = 800) -> str:
    """Simple summarization: truncate to max_chars or return the original transcript.

    For Phase 0 we keep this simple — the LLM summarizer will later combine and
    refine the transcript together with image/text context.
    """
    if not transcript:
        return ""
    if len(transcript) <= max_chars:
        return transcript
    return transcript[:max_chars] + "..."


if __name__ == '__main__':
    print('audio_api module: provides transcribe(audio_path) and summarize_transcript().')
