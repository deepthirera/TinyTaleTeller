from mcp.server.fastmcp import FastMCP, Context
from pydantic_ai.models.mcp_sampling import MCPSamplingModel
from pydantic_ai import Agent
import pandas as pd
import random
from googletrans import Translator
from enum import Enum
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_FILE_PATH = Path(__file__).parent / "data" / "validation.csv"
TOTAL_NUMBER_OF_STORIES = 201725  # Actual row count in validation.csv
TRANSLATION_TIMEOUT = 10  # seconds

class SupportedLanguage(Enum):
    TAMIL="ta"
    HINDI="hi"
    ENGLISH="en"
    
@dataclass
class StoryContext:
    current_story: Optional[str] = None
    story_id: Optional[int] = None
    last_language: Optional[SupportedLanguage] = None

mcp = FastMCP("Tiny tale teller")
translator = Translator()

async def _change_to_conversational_story(ctx: Context, original_story: str) -> str:
    SYSTEM_PROMPT = """Given a story text, change it to a conversational story for a 4 to 5 year old kid with very simple words in it to a max size of around 500 characters. Dont go beyond 500 charachters.
    Ensure the entire story is fit within 500 to 600 characters.
    Example:
    Original story:
    Crow found a pitcher and sighed, "Oh no, the water is too low for me to reach!" He spotted some pebbles nearby and thought, "I know exactly what to do."
    He dropped the pebbles into the pitcher one by one. The water rose to the top. Crow drank the cool water and felt very happy. He flew away, proud of his clever trick.

    Conversational story:
    Once upon a time, a black Crow was very thirsty. He flew all over the garden. He found a big pot of water. Crow tried to drink, but he said, "Oh no! The water is too far down. I cannot reach it."

    He looked at the ground and saw some small stones. "I have a smart idea," he said. He dropped the stones into the pot. The water came up to the top. Crow said, "Now I can drink!" He drank the cool water. He felt very happy and flew away home.
    """

    USER_PROMPT = f"""Original story:
        {original_story}

        Conversational story:"""

    logger.info("Changing to fun conversational style")
    server_agent = Agent(system_prompt=SYSTEM_PROMPT)
    try:
        result = await server_agent.run(USER_PROMPT, model=MCPSamplingModel(session=ctx.session))

        logger.info(f"Received result: {result}")
        logger.info(f"Converted to conversational style: {result.output}...")
        return result.output
    except Exception as e:
        logger.error(f"Error in create_message: {type(e).__name__}: {str(e)}")
        # Fallback to returning original story if sampling fails
        return original_story

async def _get_random_story(ctx: Context) -> str:
    try:
        if not DATA_FILE_PATH.exists():
            return f"Error: Story data file not found at {DATA_FILE_PATH}. Please ensure the data file is present."

        while True:
            random_row = random.randint(1, TOTAL_NUMBER_OF_STORIES)  # Start from 1 to avoid header
            logger.info(f"Trying to pick a random story from row {random_row}")
            story_df = pd.read_csv(
                DATA_FILE_PATH,
                skiprows=range(1, random_row + 1),
                nrows=1,
            )

            if story_df.empty or story_df['text'].isna().all():
                continue

            # Return the story as a string
            story_text = str(story_df['text'].iloc[0])
            logger.info(f"Retrieved story from row {random_row}: {story_text[:100]}...")
            break
        
        conversational_story_text = await _change_to_conversational_story(ctx, story_text)
        return conversational_story_text
    
    except Exception as e:
        logger.error(f"Unexpected error in get_random_story_in_english: {str(e)}")
        return f"Error: An unexpected error occurred while retrieving the story: {str(e)}"

@mcp.tool()
async def get_random_story_in_english(ctx: Context, dummy: str = "unused") -> str:
    """
    Retrieves a random children's story in English from a Kaggle dataset of 200K+ stories.

    This tool selects one story at random from this collection.

    Args:
        dummy: Unused parameter (for compatibility). Always use default value.

    Returns:
        str: A complete story in English, or an error message if retrieval fails.

    Example usage:
        - "Tell me a story"
        - "Give me a random story"
        - "I want to read a story in English"
    """
    logger.info(f"Inside Tool: get_random_story_in_english {dummy}")
    return await _get_random_story(ctx)
            

@mcp.tool()
async def get_story_in_other_languages(
    ctx: Context,
    lang: SupportedLanguage,
) -> str | dict[str, str]:
    """
    Translates English text (typically a story) into Tamil or Hindi.

    This tool uses Google Translate to convert English stories into Indian languages,
    making them accessible to Tamil and Hindi-speaking audiences. The translation preserves
    the narrative structure and meaning of the original story.

    Args:
        lang (SupportedLanguage): Target language - either TAMIL or HINDI

    Returns:
        str: The translated text in the target language, or an error message if translation fails.

    Supported languages:
        - TAMIL (ta): Tamil language translation
        - HINDI (hi): Hindi language translation

    Example usage:
        - "Tell me a story in Tamil" (uses specific text)
        - "Tell me a Hindi story" (agent can fetch then translate automatically)

    Note: Requires active internet connection to access Google Translate API.
    """

    try:
        logger.info(f"Inside Tool: get_story_in_other_languages - for language: {lang}")
        
        story_text = await _get_random_story(ctx)
        translated = await translator.translate(story_text, dest=lang.value)

        if not translated or not translated.text:
            logger.error(f"Error: Translation returned empty result for language '{lang.value}'.")
            return { SupportedLanguage.ENGLISH.value: story_text }
        else:
            logger.info(f"Successfully translated text to {lang.value}")
            return { SupportedLanguage.ENGLISH.value: story_text, lang.value: translated.text }

    except ConnectionError:
        return "Error: Failed to connect to translation service. Please check your internet connection."
    except TimeoutError:
        return f"Error: Translation request timed out after {TRANSLATION_TIMEOUT} seconds. Please try again."
    except Exception as e:
        logger.error(f"Unexpected error in get_translated_story: {str(e)}")
        return f"Error: Translation failed: {str(e)}"

if __name__ == "__main__":
    asyncio.run(mcp.run(transport="streamable-http"))
