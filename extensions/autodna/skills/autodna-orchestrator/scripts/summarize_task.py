#!/usr/bin/env python3
"""
Summarize user prompt into a short experiment name.
Mirrors AutoDNA's summarize_task() / plan_summarization_prompt.

Usage:
  summarize_task.py "<user_prompt>"

Output:
  Prints the short experiment name (≤10 words) to stdout.
  Also saves to ~/.openclaw/workspace/autodna_store/plan_experiment_name.txt

Environment:
  GEMINI_API_KEY  required
"""

import sys
import os
import json
import urllib.request
import urllib.error

STORE_DIR = os.path.expanduser("~/.openclaw/workspace/autodna_store")
CACHE_FILE = os.path.join(STORE_DIR, "plan_experiment_name.txt")

SUMMARIZATION_PROMPT = """\
experiment_name: The goal of the experiment with a short description (no more than 10 words).
Generate the experiment_name parameter for the following experiment description(output only the parameter value):
------------------------------
"""


def call_gemini(prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set.", file=sys.stderr)
        sys.exit(1)

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.5-flash:generateContent?key={api_key}"
    )
    payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def main():
    if len(sys.argv) < 2:
        print("Usage: summarize_task.py '<user_prompt>'", file=sys.stderr)
        sys.exit(1)

    user_prompt = sys.argv[1]

    # Check cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, encoding="utf-8") as f:
            name = f.read().strip()
        print(name)
        return

    full_prompt = SUMMARIZATION_PROMPT + user_prompt
    name = call_gemini(full_prompt)

    os.makedirs(STORE_DIR, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        f.write(name)

    print(name)


if __name__ == "__main__":
    main()
