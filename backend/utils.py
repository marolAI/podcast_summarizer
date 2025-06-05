import os
import re
import requests
import streamlit as st
import mimetypes
from urllib.parse import urlparse
from pydantic import BaseModel, Field
from typing import List, Optional


# Add common audio mimetypes
mimetypes.add_type('audio/mpeg', '.mp3')
mimetypes.add_type('audio/mp4', '.m4a')
mimetypes.add_type('audio/x-m4a', '.m4a')
mimetypes.add_type('audio/aac', '.aac')
mimetypes.add_type('audio/ogg', '.ogg')
mimetypes.add_type('audio/wav', '.wav')


SUMMARIZATION_PROMPT = """
Generate a comprehensive summary of the podcast transcript below, structured into three logical parts and formatted as a parseable JSON object.

Structure the summary content into three distinct parts:
-   Part 1: Core topic and context of the podcast.
-   Part 2: Main discussion points and arguments presented, including key examples.
-   Part 3: Conclusions reached and final takeaways for the listener.

Maintain a neutral and objective tone for all content. Avoid any promotional language or opinions not present in the transcript. Prioritize summarizing the substance and depth of the discussion over being overly brief. Ensure all information comes directly from the transcript.

Output the summary as a valid JSON object. The object should contain the following three keys, with the content for each part as their string value:
-   `core_topic_context`: string (Content for Part 1)
-   `main_points_arguments`: string (Content for Part 2)
-   `conclusions_takeaways`: string (Content for Part 3)

Output ONLY the JSON object. Do not include any other text, comments, or explanations before or after the JSON.

Transcript:
{transcript}
"""

GUEST_PROMPT = """
Analyze the following podcast transcript. Your task is to identify individuals who are actively speaking *in the transcript* as guests, distinct from the host(s) or interviewers.

Follow these strict instructions:
1.  Identify ONLY individuals who have speaking turns *within this transcript* AND are presented or can be clearly inferred from their context and speaking turns to be guests.
2.  **Crucially, do NOT include** any individuals who are only mentioned, discussed, quoted, or referred to by the host or guests, but who do NOT have their own distinct speaking turns in the transcript as participants.
3.  If the transcript does not provide sufficient information to confidently identify any individual as a guest with speaking turns (e.g., no distinct non-host speaker is evident, or the non-host speaker is never introduced or named as a guest), return an empty list `[]` for the 'guests' key.
4.  For each identified guest, extract their full name and professional title or affiliation *if* this information is explicitly provided in the transcript.
5.  If a guest is identified by speaking turn but their name or title is uncertain or not clearly stated in the transcript, note this uncertainty.
6.  Output the list of identified guests as valid JSON. The top-level key must be 'guests'. The value must be a JSON array. Each guest object within the array must contain the following keys:
    *   'name': string (The guest's full name. Use 'Unidentified Speaker' or similar if they clearly speak as a guest but their name is not found).
    *   'title': string (The guest's professional title or affiliation, or null if not found in the transcript).
    *   'verification_status': string (Use 'Verified' if name and role as guest are clear from the transcript, use 'Name Unverified' if they clearly speak as a guest but their name is unclear/missing, use 'Role Unverified' if their identity is clear but their role *as a guest* isn't fully confirmed from the transcript context - although Rule 1 should minimize this last case).
7.  Output ONLY the JSON object. Do not include any other text, comments, or explanations before or after the JSON.

Transcript:
{transcript}
"""

HIGHLIGHT_PROMPT = """
Analyze this podcast transcript and identify the most significant insights presented. The number of insights extracted should be determined naturally by the density and richness of key information in the transcript.

Identify insights based on these criteria and output them in a parseable JSON format:
1.  An insight must represent significant, novel, or a distinctly contrarian perspective presented in the discussion.
2.  Extract the core statement or summary of the insight.
3.  Extract the speaker who presented the insight.
4.  Extract the timestamp (HH:MM) indicating approximately when the insight was discussed.
5.  Order the insights chronologically based on their timestamps.

Prioritize selecting insights that are:
-   Supported by data, statistics, or studies mentioned.
-   Insights that clarify or resolve a specific question or debate.
-   Unexpected revelations or surprising pieces of information.
-   Core arguments or conclusions reached.

Output the identified insights as a valid JSON object. The structure should be a single top-level key named 'insights' which contains a JSON array. Each element in the array should be a JSON object representing a single insight, with the following keys:
-   `insight_text`: string (The core statement or summary of the insight)
-   `speaker`: string (The name or role of the speaker attributed, e.g., 'Dr. Smith', 'Host', 'Guest')
-   `timestamp`: string (The timestamp in 'HH:MM' format)

Output ONLY the JSON object. Do not include any other text, comments, or explanations before or after the JSON.

Transcript:
{transcript}
"""


class SummarizationOutputParser(BaseModel):
    """Parse summarization output."""
    core_topic_context: str = Field(description="Overall context and theme of the podcast")
    main_points_arguments: str = Field(description="Key points and arguments presented")
    conclusions_takeaways: str = Field(description="Final conclusions and key takeaways")


class Guest(BaseModel):
    name: str = Field(description="Guest's full name")
    title: Optional[str] = Field(description="Professional title")
    # verification_status: str = Field(description="Verification status")


class GuestList(BaseModel):
    guests: List[Guest] = Field(description="List of guest")


class HighlightItem(BaseModel):
    insight_text: str = Field(description="Text of the insight")
    speaker: str = Field(description="Speaker mentioned in the insight")
    timestamp: str = Field(description="Timestamp in MM:SS format")


class HighlightResult(BaseModel):
    insights: List[HighlightItem] = Field(description="List of insights")


def add_space(num_spaces=1):
    for _ in range(num_spaces):
        st.write("\n")


def sanitize_filename(url, title, content_type):
    """Create a safe filename with proper extension"""
    # Clean title
    clean_title = re.sub(r'[^\w\s-]', '', title).strip()
    clean_title = re.sub(r'[-\s]+', '_', clean_title)[:50]
    
    # Get extension from URL or content type
    path = urlparse(url).path
    ext = os.path.splitext(path)[1]
    
    if not ext or len(ext) > 5: 
        ext = mimetypes.guess_extension(content_type) or '.mp3'
    
    return f"{clean_title}{ext}"


def download_file(url, file_path):
    """Download file with progress handling"""
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


