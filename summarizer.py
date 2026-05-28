"""
YouTube Video Summarizer — Backend Module
===========================================
Handles: URL parsing, transcript fetching, text chunking, and summarization via
Mistral AI API (OpenAI-compatible endpoint).
"""

import re
import os
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter


# ── Constants ────────────────────────────────────────────────────────────────

MISTRAL_BASE_URL = "https://api.mistral.ai/v1"
MISTRAL_MODEL = "mistral-large-latest"
MAX_WORDS_PER_CHUNK = 10000                 # Mistral has large context window

SYSTEM_PROMPT = """You are a precise video summarizer. Given a YouTube transcript, respond with:
1. A one-paragraph summary of the video
2. 5 key takeaways (numbered)
3. The main topic or theme of the video

Keep each section concise and informative."""


# ── API Client ───────────────────────────────────────────────────────────────

def get_mistral_client() -> OpenAI:
    api_key = None
    try:
        import streamlit as st
        api_key = st.secrets.get("MISTRAL_API_KEY")
    except Exception:
        pass
    if not api_key:
        api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError(
            "MISTRAL_API_KEY not found. Set it in .env, Streamlit secrets, "
            "or as an environment variable."
        )
    return OpenAI(base_url=MISTRAL_BASE_URL, api_key=api_key)


# ── YouTube URL Parsing ──────────────────────────────────────────────────────

def extract_video_id(url: str) -> str | None:
    patterns = [
        r"(?:youtube\.com/watch\?.*v=)([a-zA-Z0-9_-]{11})",
        r"(?:youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"(?:youtube\.com/shorts/)([a-zA-Z0-9_-]{11})",
        r"(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
        r"(?:youtube\.com/live/)([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


# ── Transcript Fetching ──────────────────────────────────────────────────────

def fetch_transcript(video_id: str, languages: list[str] | None = None) -> str:
    if languages is None:
        languages = ["en", "hi", "es", "fr", "de", "ja", "ko", "pt", "ru", "ar"]
    transcript = YouTubeTranscriptApi().fetch(video_id, languages=languages)
    formatter = TextFormatter()
    return formatter.format_transcript(transcript)


# ── Text Chunking ────────────────────────────────────────────────────────────

def chunk_text(text: str, max_words: int = MAX_WORDS_PER_CHUNK) -> list[str]:
    words = text.split()
    if len(words) <= max_words:
        return [text]
    chunks = []
    for i in range(0, len(words), max_words):
        chunks.append(" ".join(words[i : i + max_words]))
    return chunks


# ── Mistral API Interaction ──────────────────────────────────────────────────

def summarize_chunk(client: OpenAI, chunk: str, chunk_index: int = 1, total_chunks: int = 1, model: str = MISTRAL_MODEL) -> str:
    if total_chunks == 1:
        user_msg = f"Please summarize the following YouTube transcript:\n\n{chunk}"
    else:
        user_msg = (
            f"This is part {chunk_index} of {total_chunks} of a YouTube transcript. "
            f"Please summarize this section:\n\n{chunk}"
        )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content


def merge_chunk_summaries(client: OpenAI, chunk_summaries: list[str], model: str = MISTRAL_MODEL) -> str:
    combined = "\n\n---\n\n".join(
        f"Section {i+1} summary:\n{s}" for i, s in enumerate(chunk_summaries)
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a synthesizer. Combine the following section summaries "
                           "into one cohesive final summary with: one paragraph summary, "
                           "5 key takeaways, and the main topic.",
            },
            {
                "role": "user",
                "content": f"Combine these section summaries into a single coherent summary:\n\n{combined}",
            },
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content


# ── Orchestrator ─────────────────────────────────────────────────────────────

def summarize_video(url: str) -> str:
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError(
            "Could not extract a valid YouTube video ID from the URL. "
            "Please check the link and try again."
        )
    transcript = fetch_transcript(video_id)
    chunks = chunk_text(transcript)
    client = get_mistral_client()
    if len(chunks) == 1:
        return summarize_chunk(client, chunks[0])
    chunk_summaries = []
    total = len(chunks)
    for i, chunk in enumerate(chunks, start=1):
        chunk_summaries.append(summarize_chunk(client, chunk, chunk_index=i, total_chunks=total))
    return merge_chunk_summaries(client, chunk_summaries)
