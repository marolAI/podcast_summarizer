# PODLITE


🄿🎧🄳🅻🅸🆃🅴 is an AI-driven application that streamlines podcast consumption by providing automated summaries of podcast episodes, identifying prominent guests, and highlighting key points. This project is submitted as partial fulfillment of the requirements for the [Building AI Products with OpenAI](https://uplimit.com/course/building-ai-products-with-openai) course on [Uplimit](https://uplimit.com/).

## Features

**Automated Summarization**: The app leverages the **Groq API** via the **Langchain framework** to generate concise and coherent summaries of podcast episodes. This enables users to quickly grasp the main ideas and highlights without listening to the entire episode, benefiting from Groq's high-speed inference.

**Guest Identification**: Utilizing advanced natural language processing techniques, typically orchestrated via **Langchain**, the application identifies and lists the guests featured in each podcast episode from the transcript. This feature helps users recognize episodes featuring their favorite speakers.

**Key Highlights**: The summarization process, powered by the **Groq API** through **Langchain**, also identifies and extracts key highlights and important insights from the podcast transcript. This saves users time and allows them to focus on the most valuable content.

**Accurate Transcription**: The project integrates the **Whisper model** using the efficient **`faster-whisper`** library for accurate podcast episode transcription. This ensures that the generated summaries and analysis are based on precise and reliable input derived directly from the audio.

**RSS Feed Integration**: Supports fetching episode information directly from podcast RSS feeds using the **`feedparser`** library.

## Tech Stack

This project utilizes the following key technologies and libraries:

*   **Python**: The core programming language for the application logic.
*   **Streamlit**: For building the interactive and user-friendly web interface.
*   **faster-whisper**: An optimized implementation of the Whisper model for fast and accurate audio transcription.
*   **Langchain**: A framework used to develop applications powered by language models, orchestrating workflows like summarization and information extraction.
*   **Langchain-Groq**: The specific integration layer within Langchain for connecting to and utilizing the high-speed Groq API.
*   **Groq API**: Provides the underlying large language model (LLM) inference capabilities for summarization and text analysis.
*   **feedparser**: Library used for parsing RSS feeds to retrieve podcast episode details.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/marolAI/podcast_summarizer.git
    cd podcast-summarizer
    ```
2.  Create a virtual environment (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Set up necessary environment variables. Get you `GROQ_API_KEY` [here](https://console.groq.com/keys)

## Usage

1.  Ensure your virtual environment is active.
2.  Run the Streamlit application:
    ```bash
    streamlit run app.py
    ```
3.  Open your web browser and navigate to the provided local URL (usually `http://localhost:8501`).

## License

This project is licensed under the [MIT License](license.txt).

## Contact

For questions or feedback, please contact the author:

*   **Author:** Andriamarolahy R.
*   **GitHub:** `https://github.com/marolAI`
*   **Email: marolahyrabe@gmail.com**