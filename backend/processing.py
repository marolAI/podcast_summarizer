from faster_whisper import WhisperModel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser

from backend.utils import SUMMARIZATION_PROMPT, GUEST_PROMPT, HIGHLIGHT_PROMPT, GuestList, HighlightResult,  SummarizationOutputParser


class PodcastSummarizer:
    """Podcast Summarizer object."""
    def __init__(self):
        self.model = WhisperModel("tiny", device="cpu", compute_type="int8")
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.0,
            max_retries=2,
        )

    def transcribe(self, audio_file_path: str) -> str:
        """Transcribe podcast audio.
        
        Args:
            
        Returns:
            The transcribed text.
        """
        segments, info = self.model.transcribe(audio_file_path, beam_size=5)

        transcript = ""
        for segment in segments:
            transcript += segment.text

        return transcript

    def summarize(self, transcript: str):
        summarization_prompt = ChatPromptTemplate.from_messages([("system", SUMMARIZATION_PROMPT)])
        parser = JsonOutputParser(pydantic_object=SummarizationOutputParser)
        summarization_chain = summarization_prompt | self.llm | parser
        return summarization_chain.invoke({"transcript": transcript})

    def highlight(self, transcript: str):
        highlight_prompt = ChatPromptTemplate.from_messages([("system", HIGHLIGHT_PROMPT)])
        parser = JsonOutputParser(pydantic_object=HighlightResult)
        highlight_chain = highlight_prompt | self.llm | parser
        return highlight_chain.invoke({"transcript": transcript}) 

    def get_guest_info(self, transcript: str):
        guest_prompt = ChatPromptTemplate.from_messages([("system", GUEST_PROMPT)])
        parser = PydanticOutputParser(pydantic_object=GuestList)
        guest_chain = guest_prompt | self.llm | parser
        return guest_chain.invoke({"transcript": transcript})
