"""AI provider adapters. API keys are read on the server only."""
import asyncio
import os

import httpx
from dotenv import load_dotenv

load_dotenv()


class ProviderError(Exception):
    pass


def gemini_enabled():
    return bool(os.getenv("GEMINI_API_KEY", "").strip())


def openrouter_enabled():
    return bool(os.getenv("OPENROUTER_API_KEY", "").strip())


async def gemini(prompt: str, json_output: bool = False) -> str:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        raise ProviderError("GEMINI_API_KEY is not configured.")
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash").strip() or "gemini-3.5-flash"
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.4}}
    if json_output:
        payload["generationConfig"]["responseMimeType"] = "application/json"
    last_error = ""
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            for attempt in range(3):
                    response = await client.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                        headers={"x-goog-api-key": key, "Content-Type": "application/json"}, json=payload,
                    )
                    if response.status_code in (429, 500, 502, 503, 504):
                        last_error = f"Gemini returned HTTP {response.status_code} for {model}"
                        if attempt < 2:
                            await asyncio.sleep(1.5 * (2 ** attempt))
                        continue
                    if response.status_code >= 400:
                        try:
                            message = response.json().get("error", {}).get("message", "Request rejected")
                        except ValueError:
                            message = "Request rejected"
                        if response.status_code == 404:
                            raise ProviderError(f"Gemini model {model} is unavailable for this API key (404). Check GEMINI_MODEL and the models enabled in Google AI Studio.")
                        raise ProviderError(f"Gemini rejected the request ({response.status_code}): {message}")
                    data = response.json()
                    answer = "".join(part.get("text", "") for item in data.get("candidates", [])[:1]
                                     for part in item.get("content", {}).get("parts", []))
                    if not answer.strip():
                        raise ProviderError("Gemini returned no text. Try another prompt.")
                    return answer.strip()
    except httpx.RequestError as exc:
        raise ProviderError("Could not connect to Gemini. Check your connection and try again.") from exc
    raise ProviderError(f"{last_error} after retries. Check your Gemini quota or try again shortly.")


async def openrouter(prompt: str, json_output: bool = False) -> str:
    key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not key:
        raise ProviderError("OPENROUTER_API_KEY is not configured.")
    model = os.getenv("OPENROUTER_MODEL", "openrouter/free").strip() or "openrouter/free"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
    }
    if json_output:
        payload["response_format"] = {"type": "json_object"}
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json=payload,
            )
    except httpx.RequestError as exc:
        raise ProviderError("Could not connect to OpenRouter.") from exc
    if response.status_code >= 400:
        try:
            message = response.json().get("error", {}).get("message", "Request rejected")
        except (AttributeError, TypeError, ValueError):
            message = "Request rejected"
        raise ProviderError(f"OpenRouter rejected the request ({response.status_code}): {message}")
    try:
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise ProviderError("OpenRouter returned an invalid response.") from exc
    if not isinstance(answer, str) or not answer.strip():
        raise ProviderError("OpenRouter returned no text.")
    return answer.strip()


async def complete(prompt: str, json_output: bool = False):
    try:
        return await gemini(prompt, json_output), "gemini"
    except ProviderError as gemini_error:
        try:
            return await openrouter(prompt, json_output), "openrouter"
        except ProviderError as fallback_error:
            raise ProviderError(f"Gemini failed: {gemini_error} OpenRouter fallback failed: {fallback_error}") from gemini_error
