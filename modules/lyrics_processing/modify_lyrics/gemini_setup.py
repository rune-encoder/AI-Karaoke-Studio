# Third-Party Imports
from langchain_google_genai import ChatGoogleGenerativeAI

# Local Application Imports
from .config import GEMINI_API_KEY, GEMENI_MODEL, PARSER, PREFIX, EXPECTATION, EDGE_CASES

# Initialize the Gemini model
llm = ChatGoogleGenerativeAI(
    google_api_key=GEMINI_API_KEY,
    model=GEMENI_MODEL,
    temperature=0
)


def generate_prompt(
    raw_lyrics, 
    reference_lyrics, 
    chunk_number, 
    total_chunks, 
    chunk_start_time, 
    chunk_end_time, 
    processed_words, 
    total_words,
    previous_chunk_last_word,
    previous_chunk_last_verse,
    previous_chunk_end_time,
    correction_log,
    expected_next_word
):
    PROMPT = f"""
{PREFIX}

BATCH INFORMATION STATUS:
===================
You are currently processing **chunk {chunk_number} of {total_chunks} total chunks**. 
Processed Words: {processed_words} / {total_words}

## PREVIOUS CHUNK CONTEXT:
- **Last word of previous chunk:** "{previous_chunk_last_word}"
- **Verse number of last word:** {previous_chunk_last_verse}
- **End time of last word in previous chunk:** {previous_chunk_end_time}s

## CHUNK TIMING BOUNDARIES:
- **Start Time:** {chunk_start_time}
- **End Time:** {chunk_end_time}
- The first word of this chunk must have a **start time greater than or equal to** the last word of the previous chunk.

## EXPECTED NEXT WORD:
- The next expected word in the reference lyrics after this chunk is **"{expected_next_word}"**.

## CORRECTION LOG (PREVIOUS CHUNKS):
- The following words have already been corrected in earlier chunks **(showing last 10 corrections only for relevance):**
{correction_log[-10:]}

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
1. **Do not modify or adjust start or end times under any circumstances.**
2. **Ensure each word's start time remains exactly as it is.**
3. **Every word must retain its original timing regardless of corrections.**
4. **Use the correction log to maintain consistent spelling and formatting across all chunks.**
5. **Ensure smooth transitions between chunks by respecting the last word, verse, and expected next word.**

{PARSER.get_format_instructions()}
"""
    return PROMPT