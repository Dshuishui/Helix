#!/usr/bin/env python3
"""
Judge whether an experiment is simple or complex.
Mirrors AutoDNA's judge_task_complexity() / judger_prompt.

Usage:
  judge_complexity.py "<experiment_name>"

Output:
  Prints "simple" or "complex" to stdout.
  Also saves to ~/.openclaw/workspace/autodna_store/plan_complexity.txt

Environment:
  GEMINI_API_KEY  required
"""

import sys
import os
import json
import urllib.request
import urllib.error

STORE_DIR = os.path.expanduser("~/.openclaw/workspace/autodna_store")
CACHE_FILE = os.path.join(STORE_DIR, "plan_complexity.txt")

JUDGER_PROMPT = """\
You are a judger that judges whether an experiment is simple or complex.
If an experiment composing of very different sub-experiments instead of interative loops, then it is a complex one. Otherwise, you should deem it as a simple one. Output only "simple" or "complex"(without quotes).
----------------------------------------------
The experiment:
"""


def call_gemini(prompt: str) -> str:
    import subprocess
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set.", file=sys.stderr)
        sys.exit(1)

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.5-pro:generateContent?key={api_key}"
    )
    payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]})

    proxy = (os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY") or
             os.environ.get("http_proxy") or os.environ.get("HTTP_PROXY"))
    cmd = ["curl", "-s", "--max-time", "60",
           "-H", "Content-Type: application/json",
           "-d", payload, url]
    if proxy:
        cmd = ["curl", "-s", "--max-time", "60",
               "--proxy", proxy,
               "-H", "Content-Type: application/json",
               "-d", payload, url]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"curl failed: {result.stderr}")
    data = json.loads(result.stdout)
    if "error" in data:
        err = data["error"]
        raise urllib.error.HTTPError(url, err.get("code", 0), err.get("message", "API error"), {}, None)
    return data["candidates"][0]["content"]["parts"][0]["text"].strip().lower()


def main():
    if len(sys.argv) < 2:
        print("Usage: judge_complexity.py '<experiment_name>'", file=sys.stderr)
        sys.exit(1)

    experiment_name = sys.argv[1]

    # Check cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, encoding="utf-8") as f:
            complexity = f.read().strip()
        print(complexity)
        return

    full_prompt = JUDGER_PROMPT + experiment_name
    complexity = call_gemini(full_prompt)

    # Normalize
    if "complex" in complexity:
        complexity = "complex"
    else:
        complexity = "simple"

    os.makedirs(STORE_DIR, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        f.write(complexity)

    print(complexity)


if __name__ == "__main__":
    main()
