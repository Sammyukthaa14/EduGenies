from ai_client import complete

async def explain(text: str):
    return await complete("Explain this concept simply for a student, with an example: " + text)
