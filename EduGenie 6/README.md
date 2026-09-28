# EduGenie

Gemini-first learning assistant with an OpenRouter fallback, built with FastAPI and a responsive HTML/CSS/JavaScript interface. It explains concepts, answers questions, generates three-question quizzes, summarizes passages, and suggests four-week learning paths.

## Run locally

Python 3.10+ is required. Extract the project, open the `EduGenie` folder in VS Code, and run:

```bash
python3 run.py
```

The first run creates a virtual environment, installs dependencies, and asks for a Gemini API key privately in the terminal. The key is saved in `.env`, which is excluded from Git. Open http://127.0.0.1:8001 . Press Control+C to stop. Subsequent starts use the same command. Never paste a key into chat or a public repository; rotate any key that has been exposed.

Gemini is tried first for every feature. If it fails, EduGenie uses OpenRouter's free-model router. For local development, add `OPENROUTER_API_KEY` to `.env`; on Vercel, add it under Project Settings > Environment Variables. Set `OPENROUTER_MODEL` to use a specific OpenRouter model instead of the default `openrouter/free`. The interface keeps the single `Gemini AI` product label regardless of which backend handles the request.

## Test

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Check http://127.0.0.1:8001/health and http://127.0.0.1:8001/docs . The health response reports whether both provider keys are configured. API tests mock the providers and do not spend API quota. Live results are labeled Gemini AI.

## Deploy to Vercel

1. Import the repository into Vercel. Vercel detects the FastAPI app in `main.py`.
2. In Project Settings > Environment Variables, add `GEMINI_API_KEY` and `OPENROUTER_API_KEY`. Optionally set `GEMINI_MODEL` and `OPENROUTER_MODEL`.
3. Deploy, then check `/health` to confirm both keys are configured and test the features on the deployment URL.

Do not upload `.env` or put API keys in repository files. Vercel injects environment variables into the server runtime. The API docs are at `/docs` and the status endpoint is `/health`.

## Code

- `main.py`: FastAPI routes, request validation and frontend serving.
- `ai_client.py`: server-side Gemini REST client with OpenRouter fallback.
- `explanation_module.py`, `qna.py`, `quiz_module.py`, `summary_module.py`, `learning_path.py`: feature prompts and quiz validation.
- `templates/`, `static/`: browser application.
- `run.py`: local one-command launcher.
- `tests/`: API integration checks.
