#!/usr/bin/env python3
"""
Decompose a complex experiment into ordered stages.
Mirrors AutoDNA's plan_system_prompt + plan_model.invoke() in planner_plan().

Usage:
  decompose_stages.py "<user_prompt>"

Output:
  Prints JSON stage list to stdout.
  Saves to ~/.openclaw/workspace/autodna_store/plan_stages.json

JSON format:
  [
    {"name": "DNA ...", "user_requirement": "specific params for this stage"},
    {"name": "DNA ...", "user_requirement": ""}
  ]

Environment:
  GEMINI_API_KEY  required
"""

import sys
import os
import json
import urllib.request
import urllib.error

STORE_DIR = os.path.expanduser("~/.openclaw/workspace/autodna_store")
STAGES_FILE = os.path.join(STORE_DIR, "plan_stages.json")

PLAN_SYSTEM_PROMPT = """\
You are a master planner for scientific experiments. Your task is to decompose a complex goal from a user prompt into a sequence of distinct experimental stages.

For each stage, you must identify a noun phrase 'name' starting with 'DNA' for the subtask and a 'user_requirement'. The 'user_requirement' must contain any specific data, parameters, or constraints from the initial prompt that apply ONLY to that stage. If a stage has no specific requirement, the value must be an empty string.

You must output in a JSON format like this:
[
    {
      "name": "Stage 1 Name",
      "user_requirement": "Specific parameter for stage 1."
    },
    {
      "name": "Stage 2 Name",
      "user_requirement": ""
    }
]
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
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def main():
    if len(sys.argv) < 2:
        print("Usage: decompose_stages.py '<user_prompt>'", file=sys.stderr)
        sys.exit(1)

    user_prompt = sys.argv[1]

    # Check cache
    if os.path.exists(STAGES_FILE):
        with open(STAGES_FILE, encoding="utf-8") as f:
            stages = json.load(f)
        print(json.dumps(stages, ensure_ascii=False, indent=2))
        return

    full_prompt = PLAN_SYSTEM_PROMPT + user_prompt
    raw = call_gemini(full_prompt)

    # Strip markdown fences
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        stages = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse stage JSON: {e}", file=sys.stderr)
        print(f"Raw response: {raw}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(STORE_DIR, exist_ok=True)
    with open(STAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(stages, f, ensure_ascii=False, indent=2)

    print(json.dumps(stages, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
