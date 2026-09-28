from ai_client import complete

async def answer(text: str):
    return await complete("Answer this student question accurately and concisely. State uncertainty when needed: " + text)
