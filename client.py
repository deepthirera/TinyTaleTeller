from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP
from pydantic_ai.settings import ModelSettings
from dotenv import load_dotenv
import asyncio

load_dotenv()

# model = "groq:openai/gpt-oss-120b"
# model = "google-gla:gemini-2.5-pro"
model="gemini-2.5-flash"

server = MCPServerStreamableHTTP("http://localhost:8000/mcp")

model_settings = ModelSettings(
    temperature=0.7,
    max_tokens=1000,
)

agent = Agent(
    model,
    model_settings=model_settings,
    toolsets=[server],
    system_prompt=(
        """
            You are a story telling agent that tells tiny stories in english, or bilingual english with hindi or english with tamil .
            You have tools to do this. If the user asks for a story, give back a english story.
            If they ask for astory in tamil or hindi, then use get_story_in_other_languages tool to get in the right language.
            If you receive story in two languages from tools, show both of them to user.
            Speak to the user in a childish tone. Don't change the story that you receive from tools. Show that as is to user.
            If user asks for languages other than Hindi or Tamil, say it is not supported.
        """
    ),
)


async def client_main(question: str) -> str:
    agent.set_mcp_sampling_model()
    # question = input("You can ask for story in english/tamil/hindi. What would you like? \n")
    result = await agent.run(question)

    print("User:", question)
    print("Assistant:", result.output)

    return result.output


if __name__ == "__main__":
    question = input("You can ask for story in english/tamil/hindi. What would you like? \n")
    asyncio.run(client_main(question))