# Third-Party Imports
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_google_genai import ChatGoogleGenerativeAI

# Local Application Imports
from .config import GEMINI_API_KEY, GEMENI_MODEL, PARSER, PREFIX, EXPECTATION, EDGE_CASES

# Initialize the Gemini model
llm = ChatGoogleGenerativeAI(
    google_api_key=GEMINI_API_KEY,
    model=GEMENI_MODEL,
    temperature=0
)

# Each chunk contains a subset of the raw transcribed lyrics for this task. 
# The corrected lyrics provided below represent the full song and are consistent across all chunks to ensure proper alignment.

# After each chunk is processed:
# 1. The corrected lyrics will be dynamically updated to reflect the lyrics already aligned in the previous chunks.
# 2. This ensures that each chunk focuses only on the remaining unprocessed parts of the corrected lyrics.

def generate_prompt(raw_lyrics, reference_lyrics, chunk_number, total_chunks, chunk_start_time, chunk_end_time, processed_words, total_words):
    PROMPT = f"""
{PREFIX}

BATCH INFORMATION STATUS:
===================
You are currently processing **chunk {chunk_number} of {total_chunks} total chunks**. 
Processed Words: {processed_words} / {total_words}

Your task is to align the raw transcribed lyrics in this chunk with the corrected lyrics, ensuring that the output aligns as closely as possible with the corrected lyrics while adhering to the provided constraints

CHUNK TIMING BOUNDARIES:
===================
Start Time: {chunk_start_time}
End Time: {chunk_end_time}

RAW LYRICS:
===================
{raw_lyrics}

CORRECTED LYRICS:
===================
{reference_lyrics}

EXPECTATIONS:
===================
{EXPECTATION}

EDGE CASES:
===================
{EDGE_CASES}

INSTRUCTIONS:
===================
1. Do not backtrack or reuse previous timings for subsequent words. Timing must always progress forward.
2. Ensure each word's start time is greater than or equal to the end time of the previous word.
3. If a word's timing is inconsistent or overlaps, adjust it to fit the timeline without breaking the sequence.

{PARSER.get_format_instructions()}
"""

    return PROMPT
