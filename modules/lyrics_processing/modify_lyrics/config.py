# Standard Library Imports
from typing import List
import os

# Third-Party Imports
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, RootModel

# Load environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMENI_MODEL = "gemini-1.5-flash"

# Prompt components
PREFIX = """
You are an AI tasked with aligning and correcting transcribed lyrics from a raw speech-to-text model by comparing them to the provided corrected lyrics.

The raw transcribed lyrics may contain:
- **Incorrect words**: Words that differ from the corrected lyrics.
- **Ghost words**: Words that do not exist in the corrected lyrics.
- **Split or merged words**: For example, "it's" instead of "it is" or "it is" instead of "it's."
- **Correct words**: Words that align perfectly with the corrected lyrics.

Each word in the raw transcription includes a **probability score** (ranging from 0.0 to 1.0) that indicates the model's confidence in the word's correctness:
- High scores (≥ 0.9) generally indicate the word is **correct**.
- Low scores (< 0.8) suggest the word may be **incorrect**, a **ghost word**, or misaligned.

Your primary goal is to align the raw transcribed lyrics with the corrected lyrics while adhering to the provided constraints and schema.
Use the **probability score** as a key factor in determining the correctness of words and whether to modify or remove them.
The task is critical for refining lyrics alignment for downstream applications such as karaoke timing, lyrical analysis, or music transcription. 
Your output must be highly accurate to ensure the data is usable for these purposes.
"""

EXPECTATION = """
Your task is to:
1. Correct the raw transcribed lyrics to match the provided corrected lyrics:
   - Replace **incorrect words** with their corrected counterparts.
   - Remove **ghost words** (words not present in the corrected lyrics) by leaving them as empty strings (`""`).
   - Handle **split or merged words** by including both words in the same string without modifying the start or end times. For example:
     - "it's" → "it is"
     - "cannot" → "can not"
     - "they are" → "they're"
   - Ensure that the **capitalization** and **punctuation** match the corrected lyrics exactly. Do not infer or add punctuation where it does not exist in the corrected lyrics. For example:
     - Raw: "twinkle twinkle little star"
     - Corrected: "Twinkle twinkle little star"
     - Raw: "how i wonder what you are"
     - Corrected: "How I wonder what you are"

2. Adhere to the following constraints:
   - **Do not modify the start and end times** of any words unless splitting or merging requires adjustment.
   - Use the **probability score** provided for each word to guide decisions:
     - Words with high probabilities (≥ 0.9) are likely correct.
     - Words with low probabilities (< 0.8) should be evaluated for correctness and potentially removed if they do not align with the corrected lyrics.
   - The sequence of words must match the corrected lyrics exactly, accounting for removed or modified words.
   - Ensure output is valid JSON and follows the provided schema.
"""

EDGE_CASES = """
1. If a ghost word appears, set it to an empty string (`""`) but retain its original timing:
   Raw: "hello world ghost"
   Corrected: "hello world"
   Output: [
       { "word": "hello", "start": 0.0, "end": 0.5 },
       { "word": "world", "start": 0.5, "end": 1.0 },
       { "word": "", "start": 1.0, "end": 1.5 }
   ]

2. If a word is split or merged, include both words in the same string:
   Raw: "it's a nice day"
   Corrected: "it is a nice day"
   Output: [
       { "word": "it is", "start": 0.0, "end": 0.5 },
       { "word": "a", "start": 0.5, "end": 1.0 },
       { "word": "nice", "start": 1.0, "end": 1.5 },
       { "word": "day", "start": 1.5, "end": 2.0 }
   ]

3. If a word is correct, retain it as is:
   Raw: "hello world"
   Corrected: "hello world"
   Output: [
       { "word": "hello", "start": 0.0, "end": 0.5 },
       { "word": "world", "start": 0.5, "end": 1.0 }
   ]

4. If a ghost word appears in between, leave it as an empty string:
   Raw: "hello ghost world"
   Corrected: "hello world"
   Output: [
       { "word": "hello", "start": 0.0, "end": 0.5 },
       { "word": "", "start": 0.5, "end": 1.0 },
       { "word": "world", "start": 1.0, "end": 1.5 }
   ]
"""

# Define the WordAlignment schema
class WordAlignment(BaseModel):
    word: str = Field(..., description="The word from the lyrics.")
    start: float = Field(
        ...,
        description="The start time of the word in seconds. Adjust only if the corrected lyrics require word splitting or merging."
    )
    end: float = Field(
        ...,
        description="The end time of the word in seconds. Adjust only if the corrected lyrics require word splitting or merging."
    )

# Define a schema for a list of WordAlignment objects
class WordAlignmentList(RootModel):
    root: List[WordAlignment]


# Initialize the parser
PARSER = PydanticOutputParser(pydantic_object=WordAlignmentList)
