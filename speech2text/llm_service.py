
import google.generativeai as genai
from speech2text.config import GEMINI_API_KEY
from speech2text.logger_setup import log

# Configure the generative AI model
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_model():
    """Initializes and returns the generative model."""
    if not GEMINI_API_KEY:
        log.error("[bold red]GEMINI_API_KEY environment variable not set.[/bold red]")
        return None
    return genai.GenerativeModel('gemini-1.5-flash')

# --- Prompts ---

CORRECTION_PROMPT = """
Your task is to correct a raw text transcription in Spanish.
Please perform the following actions:
1. Correct any grammatical errors.
2. Fix spelling mistakes.
3. Add appropriate punctuation (commas, periods, etc.).
4. Do NOT change the content or meaning.
5. Return only the corrected text, with no extra explanations or formatting.

Here is the raw text:
---
{text_chunk}
---
"""

INITIAL_STRUCTURE_PROMPT = """
You are a text-processing assistant. Your task is to take the following text and begin structuring it into a Markdown document in Spanish.

Please perform the following actions:
1. Identify the main topic or section in this initial piece of text.
2. Create a descriptive title for this section using a Markdown heading (e.g., ## Title).
3. Organize the content in a logical and readable manner under the title.
4. Ensure the final output is only the processed Markdown content.

Here is the text:
---
{text_chunk}
---
"""

ITERATIVE_JOIN_PROMPT = """
You are a text-processing assistant continuing to build a Markdown document in spanish.
You will be given the last few words of the existing document and a new chunk of text.
Your task is to seamlessly integrate the new chunk.

Please perform the following actions:
1. Analyze the new chunk in the context of the previous text.
2. Decide if the new chunk continues the previous topic or starts a new one.
3. If it starts a new topic, create a descriptive Markdown title (e.g., ## New Topic Title).
4. Structure the new chunk's content logically.
5. Ensure there is a natural transition from the previous text.
6. **Return ONLY the newly structured content for the new chunk.** Do not repeat the previous context.

Previous context (last ~100 words of the document):
---
{previous_context}
---

New text chunk to structure and append:
---
{new_chunk}
---
"""

# --- Service Functions ---

def correct_text_chunk(text_chunk: str) -> str:
    """Uses the LLM to correct a single chunk of text."""
    model = get_model()
    if not model:
        return ""

    try:
        log.debug(f"Sending chunk for correction: {text_chunk[:100]}...")
        prompt = CORRECTION_PROMPT.format(text_chunk=text_chunk)
        response = model.generate_content(prompt)
        corrected_text = response.text.strip()
        log.debug(f"Received corrected chunk: {corrected_text[:100]}...")
        return corrected_text
    except Exception as e:
        log.error(f"[bold red]Error during text correction LLM call:[/bold red] {e}")
        return ""

def structure_initial_chunk(text_chunk: str) -> str:
    """Uses the LLM to structure the very first chunk of the document."""
    model = get_model()
    if not model:
        return ""

    try:
        log.debug(f"Sending initial chunk for structuring: {text_chunk[:100]}...")
        prompt = INITIAL_STRUCTURE_PROMPT.format(text_chunk=text_chunk)
        response = model.generate_content(prompt)
        structured_doc = response.text.strip()
        log.debug(f"Received initial structured document: {structured_doc[:150]}...")
        return structured_doc
    except Exception as e:
        log.error(f"[bold red]Error during initial structuring LLM call:[/bold red] {e}")
        return ""

def structure_and_join_chunk(previous_context: str, new_chunk: str) -> str:
    """Uses the LLM to structure a new chunk and join it to the document."""
    model = get_model()
    if not model:
        return ""

    try:
        log.debug(f"Sending new chunk for iterative join: {new_chunk[:100]}...")
        prompt = ITERATIVE_JOIN_PROMPT.format(
            previous_context=previous_context,
            new_chunk=new_chunk
        )
        response = model.generate_content(prompt)
        newly_structured_text = response.text.strip()
        log.debug(f"Received newly structured text: {newly_structured_text[:150]}...")
        return newly_structured_text
    except Exception as e:
        log.error(f"[bold red]Error during iterative join LLM call:[/bold red] {e}")
        return ""
