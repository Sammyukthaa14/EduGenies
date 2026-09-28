"""Explicit no-key demonstration, with no claim of generated factual accuracy."""
import re


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]


def respond(task, content, level="beginner"):
    lines = sentences(content)
    if task == "summarize":
        if len(lines) < 2:
            return "Demo summary (extractive): " + content.strip()
        return "Demo summary (extractive): " + " ".join(lines[:min(3, len(lines))])
    if task == "recommendations":
        return (f"Demo learning plan for {content.strip()} ({level}):\n"
                "Week 1: Learn core terms and definitions.\n"
                "Week 2: Work through a beginner lesson and take notes.\n"
                "Week 3: Solve practice exercises and review mistakes.\n"
                "Week 4: Build a small project and explain what you learned.\n"
                "Resources: library textbooks, university course pages, and practice problems.")
    if task == "qa":
        return "Demo mode cannot verify factual answers. Configure Gemini and OpenRouter API keys for AI Q&A, or provide source text and use Summary."
    return ("Demo explanation: " + content.strip() + "\n\n"
            "Break the topic into key terms, find one concrete example, and check your understanding with practice questions. "
            "Configure Gemini and OpenRouter API keys for AI-generated explanations.")


def quiz(content):
    source = sentences(content)
    return [{"question": f"Which statement appears in the supplied text? (Question {n})",
             "options": [source[(n - 1) % len(source)], "No information is provided.",
                         "The text discusses an unrelated subject.", "All statements are identical."],
             "answer": source[(n - 1) % len(source)]} for n in range(1, 4)]
