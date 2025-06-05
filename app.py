import os
import json
import torch
import feedparser
import streamlit as st

from backend.utils import add_space, sanitize_filename, download_file
from backend.processing import PodcastSummarizer

torch.classes.__path__ = [] # RuntimeError: Tried to instantiate class '__path__._path', but it does not exist!


st.set_page_config(page_icon="🎧", layout="wide", page_title="Castbrief")

# Initialize session state variables
if "file_path" not in st.session_state:
    st.session_state.file_path = None
if "podcasts" not in st.session_state:
    st.session_state.podcasts = {}
if "summarizer" not in st.session_state:
    st.session_state.summarizer = PodcastSummarizer()

custom_headers = {
                "core_topic_context": "Core Topic",
                "main_points_arguments": "Discussion Points",
                "conclusions_takeaways": "Summary"
            }


def display_sidebar():
    """Render the sidebar components"""
    with st.sidebar:
        st.header("Castbrief")
        st.markdown("""Podcast Summarizer condenses lengthy podcast episodes into concise summaries.""")
        st.markdown(
            """
                [![source code](https://img.shields.io/badge/view_source_code-gray?logo=github)](https://github.com/marolAI/podcast_summarizer/blob/master/app.py)
                
                🔍[More projects](https://marolai.github.io/projects/)
            """
        )
        st.divider()
        add_space(10)
        
        # Provide instructions or context
        st.write("Enter the RSS feed URL of the podcast you want to summarize.\n Then press ⤶.")
        
        st.write("A sample URL is provided below to get you started.")
        # Input field for RSS feed
        feed_url = st.text_input(
            "Podcast RSS Feed URL:",
            value="https://media.rss.com/thepodcastai/feed.xml",   
            help="Paste the RSS feed URL here. The sample URL is pre-filled." 
        )
        
        if feed_url:
            with st.spinner("Searching for podcasts..."):
                parse_feed(feed_url)

        # Podcast selection dropdown
        selected_podcast = st.selectbox(
            "Available podcasts for this feed:", 
            options=st.session_state.podcasts.keys(), 
            index=None,
            placeholder="Select a Podcast to process"
        )
        
        # Download audio when podcast is selected
        if selected_podcast:
            entry = st.session_state.podcasts[selected_podcast]
            st.session_state.episode_image = entry.get("image", {}).get("href", "")
            st.session_state.episode_title = entry.get("title", "")
            with st.spinner("Downloading podcast audio..."):
                download_podcast_audio(entry)
    
        return st.button("Process Podcast Episode")
    

def parse_feed(feed_url: str):
    """Parse RSS feed and store episodes in session state"""
    try:
        feed = feedparser.parse(feed_url)
        if feed.bozo:
            st.error(f"Error parsing feed: {feed.bozo_exception}")
            return
        
        st.session_state.podcasts = {
            entry.title: entry for entry in feed.entries
        }
        
    except Exception as e:
        st.error(f"Feed processing error: {str(e)}")


def download_podcast_audio(entry: dict):
    """Download selected podcast audio and store path in session state"""
    try:
        for enclosure in entry.get('enclosures', []):
            if enclosure.get('type', '').startswith('audio/'):
                audio_url = enclosure['href']
                file_name = sanitize_filename(
                    url=audio_url,
                    title=entry.get('title', 'audio'),
                    content_type=enclosure['type']
                )
                file_path = os.path.join("./tmp", file_name)
                download_file(audio_url, file_path)
                
                # Store path in session state
                st.session_state.file_path = file_path
                # st.success(f"Downloaded: {file_name}")
                break
                
    except Exception as e:
        st.error(f"Download error: {str(e)}")
        st.session_state.file_path = None

process_button = display_sidebar()
add_space(5)
with st.sidebar:
    st.caption("Built with ❤️ using Streamlit, Whisper, and Groq")
    st.caption(f"v1.0 | 2025")

placeholder = st.empty()

with placeholder.container():
    with open("./sample_episode/podcast-1.json", 'r') as file:
        podcast_info = json.load(file)

    main_col1, main_col2 = st.columns([1, 1])
    with main_col1:
        head_col1, head_col2 = st.columns([2, 8])
        with head_col1:
            st.image(podcast_info.get("episode_image"), width=200)
        with head_col2:
            st.write("**Episode Title:**", podcast_info.get("episode_title"))
            st.write("**Guest:**", podcast_info.get("guest_info"))

        for part_title, summary in podcast_info.get("summarization_result").items():
            st.subheader(custom_headers.get(part_title, part_title.strip().title()))
            st.write(summary.strip())

    with main_col2:
        st.subheader("Key Moments")
        for highlights in podcast_info.get("highlight_result").values():
            highlight_lines = []
            for highlight in highlights:
                speaker = highlight.get('speaker', 'Unknown Speaker').strip()
                insight = highlight.get('insight_text', 'No insight text').strip()
                highlight_lines.append(f"- **{speaker}:** {insight}")

            st.markdown("\n".join(highlight_lines))


if process_button and st.session_state.file_path:
    placeholder.empty()
    with placeholder.container():
        try:
            with st.spinner("Transcribing podcast episode..."):
                st.session_state.transcript = st.session_state.summarizer.transcribe(st.session_state.file_path)
            with st.spinner("Highlighting key moments..."):
                st.session_state.highlight_result = st.session_state.summarizer.highlight(st.session_state.transcript)
            with st.spinner("Summarizing podcast episode..."):
                st.session_state.summarization_result = st.session_state.summarizer.summarize(st.session_state.transcript)
            with st.spinner("Getting the guest info..."):
                st.session_state.guest_info = st.session_state.summarizer.get_guest_info(st.session_state.transcript)
        finally:
            os.remove(st.session_state.file_path)

    with placeholder.container():
        main_col1, main_col2 = st.columns([1, 1])

        with main_col1:
            head_col1, head_col2 = st.columns([2, 8])
            with head_col1:
                if st.session_state.episode_image:
                    st.image(st.session_state.episode_image, width=200)
                else:
                    st.image("./assets/podcast_summarizer.png", width=200)

            with head_col2:
                st.write("**Episode Title:**", st.session_state.episode_title)
                st.write("**Guest:**", ", ".join([f"{guest.name}| {guest.title}" for guest in  st.session_state.guest_info.guests]))

            for part_title, summary in st.session_state.summarization_result.items():
                st.subheader(custom_headers.get(part_title, part_title.strip().title()))
                st.write(summary.strip())

        with main_col2:
            st.subheader("Key Moments")
            for highlights in st.session_state.highlight_result.values():
                highlight_lines = []
                for highlight in highlights:
                    speaker = highlight.get('speaker', 'Unknown Speaker').strip()
                    insight = highlight.get('insight_text', 'No insight text').strip()
                    highlight_lines.append(f"- **{speaker}:** {insight}")

                st.markdown("\n".join(highlight_lines))