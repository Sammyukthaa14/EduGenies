"""EduGenie FastAPI application. Run: uvicorn main:app --reload"""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel, Field

from ai_client import ProviderError, gemini_enabled, openrouter_enabled
from explanation_module import explain
from learning_path import get_learning_recommendations
from qna import answer
from quiz_module import generate_quiz
from summary_module import summarize

ROOT = Path(__file__).resolve().parent
app = FastAPI(title="EduGenie", version="1.0.0")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
templates = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape(["html"]))


class TextInput(BaseModel):
    text: str = Field(min_length=2, max_length=12000)


class LearningInput(BaseModel):
    topic: str = Field(min_length=2, max_length=500)
    level: str = Field(default="beginner", pattern="^(beginner|intermediate|advanced)$")


@app.get("/", response_class=HTMLResponse)
def index():
    return templates.get_template("index.html").render()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "gemini_configured": gemini_enabled(),
        "openrouter_configured": openrouter_enabled(),
    }


async def wrap(coro):
    try:
        return await coro
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/explain")
async def explanation(request: TextInput):
    result, provider = await wrap(explain(request.text))
    return {"result": result, "provider": provider}


@app.post("/qa")
async def question(request: TextInput):
    result, provider = await wrap(answer(request.text))
    return {"result": result, "provider": provider}


@app.post("/summarize")
async def summary(request: TextInput):
    result, provider = await wrap(summarize(request.text))
    return {"result": result, "provider": provider}


@app.post("/quiz")
async def quiz(request: TextInput):
    questions, provider = await wrap(generate_quiz(request.text))
    return {"questions": questions, "provider": provider}


@app.post("/learn/recommendations")
async def recommendations(request: LearningInput):
    result, provider = await wrap(get_learning_recommendations(request.topic, request.level))
    return {"result": result, "provider": provider}
