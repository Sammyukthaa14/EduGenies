from ai_client import complete

async def get_learning_recommendations(topic: str, level: str):
    return await complete(f"Create a four-week learning path for a {level} studying {topic}. Include weekly concepts, activities, and types of useful resources. Do not invent URLs.")
