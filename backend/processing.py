
import gc
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser

from backend.utils import SUMMARIZATION_PROMPT, GUEST_PROMPT, HIGHLIGHT_PROMPT, GuestList, HighlightResult,  SummarizationOutputParser


class PodcastSummarizer:
    """Podcast Summarizer object."""
    def __init__(self):
        self.model = None  
        self.llm = None 
        self.chains = {}

    def get_whisper_model(self):
        if self.model is None:
            from faster_whisper import WhisperModel 
            self.model = WhisperModel("tiny", device="cpu", compute_type="int8")
        return self.model

    def get_llm(self):
        if self.llm is None:
            from langchain_groq import ChatGroq 
            self.llm = ChatGroq(
                model="llama-3.1-8b-instant",
                temperature=0.0,
                max_retries=2,
            )
        return self.llm
    
    def get_chain(self, chain_type):
        llm = self.get_llm()
        if chain_type not in self.chains:
            if chain_type == "summarize":
                prompt = ChatPromptTemplate.from_messages([("system", SUMMARIZATION_PROMPT)])
                parser = JsonOutputParser(pydantic_object=SummarizationOutputParser)
                self.chains[chain_type] = prompt | llm | parser
            elif chain_type == "highlight":
                prompt = ChatPromptTemplate.from_messages([("system", HIGHLIGHT_PROMPT)])
                parser = JsonOutputParser(pydantic_object=HighlightResult)
                self.chains[chain_type] = prompt | llm | parser
            elif chain_type == "guest":
                prompt = ChatPromptTemplate.from_messages([("system", GUEST_PROMPT)])
                parser = PydanticOutputParser(pydantic_object=GuestList)
                self.chains[chain_type] = prompt | llm | parser

        return self.chains[chain_type]

    @st.cache_data(max_entries=3, ttl=3600) 
    def transcribe(_self, audio_file_path: str) -> str:
        """Transcribe podcast audio.
        
        Args:
            
        Returns:
            The transcribed text.
        """
        model = _self.get_whisper_model()
        segments, _ = model.transcribe(audio_file_path, beam_size=3, vad_filter=True)

        # Write incrementally to avoid large in-memory strings
        transcript_path = f"{audio_file_path}.txt"
        with open(transcript_path, "w", encoding="utf-8") as f:
            for segment in segments:
                f.write(segment.text + " ")
    
        return transcript_path

    @st.cache_data(max_entries=3, ttl=3600)
    def summarize(_self, transcript_path: str):
        with open(transcript_path, "r") as f:
            transcript = f.read()
        
        summarization_chain = _self.get_chain("summarize")
        return summarization_chain.invoke({"transcript": transcript})

    def highlight(self, transcript_path: str):
        with open(transcript_path, "r") as f:
            transcript = f.read()

        highlight_chain = self.get_chain("highlight")
        return highlight_chain.invoke({"transcript": transcript}) 

    def get_guest_info(self, transcript_path: str):
        with open(transcript_path, "r") as f:
            transcript = f.read()

        guest_chain = self.get_chain("guest")
        return guest_chain.invoke({"transcript": transcript})
    
    def cleanup(self):
        if self.model:
            del self.model
            self.model = None
        if self.llm:
            del self.llm
            self.llm = None
        gc.collect()
