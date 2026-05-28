"""
YouTube Video Summarizer — Streamlit Frontend
==============================================
Provides a clean UI where users paste a YouTube URL, click "Summarize",
and see a formatted summary (paragraph, takeaways, topic).
"""

import streamlit as st
from dotenv import load_dotenv

from summarizer import summarize_video

load_dotenv()

st.set_page_config(
    page_title="YouTube Video Summarizer",
    page_icon="🎥",
    layout="centered",
)

st.title("🎥 YouTube Video Summarizer")
st.markdown(
    "Paste a YouTube link below and get a **one-paragraph summary**, "
    "**5 key takeaways**, and the **main topic** — powered by Mistral AI."
)

url = st.text_input(
    "YouTube URL",
    placeholder="https://www.youtube.com/watch?v=...",
    label_visibility="collapsed",
)

summarize_clicked = st.button("✨ Summarize", type="primary", use_container_width=True)

if summarize_clicked and url:
    with st.spinner("🔍 Fetching transcript and generating summary..."):
        try:
            result = summarize_video(url)
            st.divider()
            st.subheader("📄 Summary")
            paragraphs = result.strip().split("\n\n")
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                if para[0].isdigit() and ". " in para[:4]:
                    st.markdown("#### 📌 Key Takeaways")
                    st.markdown(para)
                elif para.lower().startswith("main topic") or para.lower().startswith(
                    "**main topic"
                ):
                    st.markdown("#### 🏷️ Main Topic")
                    st.markdown(para)
                else:
                    st.markdown("#### 📝 Overview")
                    st.markdown(para)

        except ValueError as e:
            st.error(f"❌ {e}")
        except Exception as e:
            err_msg = str(e)
            if "quota" in err_msg.lower() or "429" in err_msg:
                st.error("❌ Mistral API quota exceeded.")
                st.info(
                    "The API key has hit its rate limit or daily quota.\n\n"
                    "**Wait a minute and retry**, or get a fresh key at:\n"
                    "https://console.mistral.ai/api-keys/"
                )
            elif "api key" in err_msg.lower() or "not found" in err_msg.lower():
                st.error(f"❌ {err_msg}")
            else:
                st.error(f"❌ {err_msg}")
                st.info(
                    "Possible causes:\n"
                    "- The video has no captions/transcript available\n"
                    "- The API key is missing or invalid\n"
                    "- Network connectivity issues"
                )

elif summarize_clicked and not url:
    st.warning("⚠️ Please enter a YouTube URL first.")

st.divider()
st.caption(
    "Built with Streamlit · youtube-transcript-api · Mistral AI · "
    "[Source code]"
)
