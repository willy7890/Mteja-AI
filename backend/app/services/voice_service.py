from pathlib import Path

import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class VoiceProcessingError(Exception):
    """Raised when a voice provider cannot process audio."""


async def transcribe_audio(file_path: str, filename: str) -> str:
    if not settings.OPENAI_API_KEY:
        raise VoiceProcessingError("Voice transcription is not configured")
    try:
        async with httpx.AsyncClient(base_url=settings.OPENAI_BASE_URL, timeout=90) as client:
            with Path(file_path).open("rb") as audio_file:
                response = await client.post(
                    "/audio/transcriptions",
                    headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                    data={"model": settings.VOICE_TRANSCRIPTION_MODEL},
                    files={"file": (filename, audio_file, "application/octet-stream")},
                )
            response.raise_for_status()
            text = response.json().get("text", "").strip()
            if not text:
                raise VoiceProcessingError("The audio did not contain recognizable speech")
            return text
    except VoiceProcessingError:
        raise
    except (httpx.HTTPError, OSError, ValueError) as exc:
        raise VoiceProcessingError("Voice transcription failed") from exc


async def synthesize_speech(text: str, output_path: str) -> None:
    if not settings.OPENAI_API_KEY:
        raise VoiceProcessingError("Voice synthesis is not configured")
    try:
        async with httpx.AsyncClient(base_url=settings.OPENAI_BASE_URL, timeout=90) as client:
            response = await client.post(
                "/audio/speech",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.VOICE_TTS_MODEL,
                    "voice": settings.VOICE_TTS_VOICE,
                    "input": text,
                    "response_format": "mp3",
                },
            )
            response.raise_for_status()
            Path(output_path).write_bytes(response.content)
    except (httpx.HTTPError, OSError) as exc:
        raise VoiceProcessingError("Voice synthesis failed") from exc


def voice_http_error(error: VoiceProcessingError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error))