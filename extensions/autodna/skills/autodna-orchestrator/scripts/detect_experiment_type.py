#!/usr/bin/env python3
"""
Detect experiment type from user prompt.
Mirrors AutoDNA's get_experiment_type() + choose_system_prompt() logic.

Usage:
  detect_experiment_type.py "<user_prompt>"

Output:
  Prints one of: "storage_write", "storage_read", "storage", "default"
  - "storage_write" → DNA Storage Write: EPA_storage_prompt + save write_summary after all stages
  - "storage_read"  → DNA Storage Read:  EPA_storage_prompt + load write_summary as initial context
  - "storage"       → other DNA storage experiments: EPA_storage_prompt only
  - "default"       → all other experiments: EPA_guidance_prompt (free ReAct)
  Also saves to ~/.openclaw/workspace/autodna_store/plan_experiment_type.txt

Environment:
  GEMINI_API_KEY  required
"""

import sys
import os
import json
import urllib.request
import urllib.error

STORE_DIR = os.path.expanduser("~/.openclaw/workspace/autodna_store")
CACHE_FILE = os.path.join(STORE_DIR, "plan_experiment_type.txt")

DETECT_PROMPT = """\
You are a scientific experiment classifier. Based on the user's experiment description, determine the experiment category.

Categories:
- "storage_write": DNA Storage Write — encoding/writing data into DNA molecules
- "storage_read": DNA Storage Read — decoding/reading data from previously stored DNA
- "storage": other DNA storage experiments (not specifically write or read)
- "rpa": Recombinase Polymerase Amplification experiments
- "default": RNA experiments, DNA synthesis, PCR amplification, detection assays, or any other experiment type

Output ONLY one of these five strings (without quotes): storage_write, storage_read, storage, rpa, default

User experiment description:
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
        print("Usage: detect_experiment_type.py '<user_prompt>'", file=sys.stderr)
        sys.exit(1)

    user_prompt = sys.argv[1]

    # Check cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, encoding="utf-8") as f:
            exp_type = f.read().strip()
        print(exp_type)
        return

    full_prompt = DETECT_PROMPT + user_prompt
    raw = call_gemini(full_prompt)

    # Normalize to one of the five valid values
    if "storage_write" in raw or ("write" in raw and "storage" in raw):
        exp_type = "storage_write"
    elif "storage_read" in raw or ("read" in raw and "storage" in raw):
        exp_type = "storage_read"
    elif "storage" in raw:
        exp_type = "storage"
    elif "rpa" in raw:
        exp_type = "rpa"
    else:
        exp_type = "default"

    os.makedirs(STORE_DIR, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        f.write(exp_type)

    print(exp_type)


if __name__ == "__main__":
    main()
