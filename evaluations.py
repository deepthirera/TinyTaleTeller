from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import LLMJudge
from typing import Any
from client import client_main

model = "google-gla:gemini-2.5-pro"
dataset = Dataset[str, str, Any](
    cases=[
        Case(
            name="english_story",
            inputs="Tell me a english story",
            expected_output=None,
            evaluators=(
                LLMJudge(
                    model=model,
                    rubric="Should a short story in english",
                    include_input=True,
                ),
            ),
        ),
        Case(
            name="tamil_story",
            inputs="Tell me a tamil story",
            expected_output=None,
            evaluators=(
                LLMJudge(
                    model=model,
                    rubric="Should have a short story in english and the same translated in tamil",
                    include_input=True,
                ),
            ),
        ),
        Case(
            name="hindi_story",
            inputs="A hindi story?",
            expected_output=None,
            evaluators=(
                LLMJudge(
                    model=model,
                    rubric="Should have a short story in english and the same translated in hindi",
                    include_input=True,
                ),
            ),
        ),
        Case(
            name="latin_story",
            inputs="A latin story?",
            expected_output=None,
            evaluators=(
                LLMJudge(
                    model=model,
                    rubric="Should reply saying it can only say tamil, hindi or english stories",
                    include_input=True,
                ),
            ),
        ),
        ],
    evaluators=[],
)

if __name__ == "__main__":
    import asyncio
    report = asyncio.run(dataset.evaluate(client_main))
    report.print()
