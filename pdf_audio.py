"""
PDF Audio Reader & Text-to-Speech Engine for OmniDoc Studio Pro.
Extracts narrative text from PDF documents and generates high-fidelity audio (MP3)
using gTTS and embedded speech players.
"""

import io
from typing import Dict, Any, Optional
from pypdf import PdfReader

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    gTTS = None
    GTTS_AVAILABLE = False


def extract_text_for_speech(
    pdf_bytes: bytes,
    start_page: int = 1,
    end_page: Optional[int] = None
) -> Dict[str, Any]:
    """
    Extracts text from specified page ranges for speech synthesis.
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    total_pages = len(reader.pages)

    sp = max(1, start_page)
    ep = min(total_pages, end_page if end_page is not None else total_pages)

    extracted_parts = []
    total_words = 0

    for idx in range(sp - 1, ep):
        page_text = reader.pages[idx].extract_text() or ""
        clean = page_text.strip()
        if clean:
            extracted_parts.append(f"Page {idx + 1}. {clean}")
            total_words += len(clean.split())

    full_text = "\n\n".join(extracted_parts)

    return {
        "text": full_text,
        "total_words": total_words,
        "start_page": sp,
        "end_page": ep,
        "total_doc_pages": total_pages,
        "est_duration_mins": round(total_words / 150.0, 1)  # average speaking rate ~150 wpm
    }


def generate_speech_audio(
    text: str,
    lang: str = "en",
    tld: str = "com",
    slow: bool = False,
    max_chars: int = 50000
) -> Dict[str, Any]:
    """
    Synthesizes speech from text using gTTS and returns MP3 bytes.
    """
    if not GTTS_AVAILABLE:
        raise RuntimeError("gTTS library is not available. Please install gTTS.")

    if not text or not text.strip():
        raise ValueError("No text provided to synthesize audio.")

    # Truncate text if exceeds safety limits
    trimmed_text = text[:max_chars].strip()

    tts = gTTS(text=trimmed_text, lang=lang, tld=tld, slow=slow)
    audio_stream = io.BytesIO()
    tts.write_to_fp(audio_stream)
    audio_bytes = audio_stream.getvalue()

    return {
        "audio_bytes": audio_bytes,
        "mime_type": "audio/mp3",
        "char_count": len(trimmed_text),
        "size_bytes": len(audio_bytes),
        "filename": "document_narration.mp3"
    }
