# 🎥 YouTube Video Summarizer

Paste a YouTube link, get a **one-paragraph summary**, **5 key takeaways**, and the **main topic** — powered by Mistral AI.

## Features

- Supports YouTube URLs (`/watch`, `/shorts`, `/embed`, `/live`, `youtu.be`)
- Auto-detects transcript language (English, Hindi, Spanish, French, German, Japanese, Korean, Portuguese, Russian, Arabic)
- Chunks long transcripts automatically (handles hour-long videos)
- Clean Streamlit UI with formatted output

## Prerequisites

- Python 3.10+
- A [Mistral AI API key](https://console.mistral.ai/api-keys/)

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/haideralio73/youtube-video-summarizer.git
cd youtube-video-summarizer

# 2. Create a virtual environment (optional but recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your API key
#    Option A: Create a .env file
cp .env.example .env
# Then edit .env and add your key:
#   MISTRAL_API_KEY=your_key_here

#    Option B: Set environment variable directly
#   Windows:   set MISTRAL_API_KEY=your_key_here
#   macOS/Linux: export MISTRAL_API_KEY=your_key_here
```

## Run

```bash
streamlit run app.py
```

Open the URL shown in your terminal (default: `http://localhost:8501`).



## How it works

1. Extracts the video ID from the URL
2. Fetches the transcript via `youtube-transcript-api` (with multi-language fallback)
3. Chunks the transcript if it exceeds 10,000 words
4. Sends each chunk to Mistral AI for summarization
5. Merges chunk summaries into one final result
