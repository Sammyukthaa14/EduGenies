"""One-command setup and startup: python3 run.py"""
import getpass
import os
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / ".env"
VENV = ROOT / ".venv"
PYTHON = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def configure():
    existing = ENV_FILE.read_text().splitlines() if ENV_FILE.exists() else []
    configured = any(row.startswith("GEMINI_API_KEY=") and row.partition("=")[2].strip() for row in existing)
    if not configured:
        print("Enter your Gemini API key locally. Input is hidden. This project requires Gemini.")
        key = getpass.getpass("Gemini API key: ").strip()
        if not key:
            sys.exit("Gemini API key is required. Start again and enter your key.")
        if key:
            existing = [row for row in existing if not row.startswith("GEMINI_API_KEY=")]
            ENV_FILE.write_text("\n".join(existing + ["GEMINI_API_KEY=" + key]) + "\n")
            try:
                ENV_FILE.chmod(0o600)
            except OSError:
                pass


def main():
    if not (ROOT / "main.py").is_file():
        sys.exit("EduGenie/main.py is missing. Extract the complete ZIP first.")
    configure()
    if not PYTHON.exists():
        print("Creating local Python environment...")
        venv.create(VENV, with_pip=True)
    print("Installing required packages (this may take a minute on first run)...")
    subprocess.run([str(PYTHON), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")], cwd=ROOT, check=True)
    print("Open http://127.0.0.1:8001 in your browser. Press Control+C to stop.")
    subprocess.run([str(PYTHON), "-m", "uvicorn", "main:app", "--reload", "--host", "127.0.0.1", "--port", "8001"], cwd=ROOT, check=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
    except subprocess.CalledProcessError as exc:
        sys.exit(f"Setup or launch failed (exit {exc.returncode}). See the error above.")
