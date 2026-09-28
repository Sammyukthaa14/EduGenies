from ai_client import complete

async def summarize(text: str):
    return await complete("Summarize in 3-5 sentences, preserving key facts:\n" + text)
