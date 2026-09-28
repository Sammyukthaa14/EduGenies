import json
from ai_client import ProviderError, complete


def validate_quiz(data):
    if isinstance(data, dict):
        data = data.get("questions")
    if not isinstance(data, list) or len(data) != 3:
        raise ProviderError("Gemini returned an invalid quiz. Please try again.")
    output = []
    for item in data:
        if not isinstance(item, dict) or not isinstance(item.get("question"), str):
            raise ProviderError("Gemini returned an invalid quiz. Please try again.")
        options, answer = item.get("options"), item.get("answer")
        if (not isinstance(options, list) or len(options) != 4 or
                any(not isinstance(option, str) or not option.strip() for option in options) or
                len(set(options)) != 4 or answer not in options):
            raise ProviderError("Gemini returned an invalid quiz. Please try again.")
        output.append({"question": item["question"], "options": options, "answer": answer})
    return output


async def generate_quiz(text: str):
    result, provider = await complete("Create exactly 3 multiple choice questions on this text/topic. Each has 4 distinct options and an answer equal to one option verbatim. Return ONLY a JSON array of objects with keys question, options, answer. Text/topic:\n" + text, json_output=True)
    try:
        return validate_quiz(json.loads(result)), provider
    except ValueError as exc:
        raise ProviderError("Gemini returned invalid JSON for the quiz. Please try again.") from exc
