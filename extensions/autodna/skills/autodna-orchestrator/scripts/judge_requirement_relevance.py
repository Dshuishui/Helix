#!/usr/bin/env python3
"""
Judge if the previous stage's user_requirement should carry over to the current stage.
Mirrors AutoDNA's judge_requirement_relevance() in ai_scientist.py.

Usage:
  judge_requirement_relevance.py <current_stage_num> \
    "<prev_stage_name>" "<prev_requirement>" "<current_stage_name>"

  current_stage_num: 1-indexed (must be ≥ 2)
  prev_stage_name:   name of the previous stage
  prev_requirement:  the user_requirement string from the previous stage (may be empty)
  current_stage_name: name of the current stage

Output:
  Prints "yes" or "no".
  - "yes"  → caller should append prev_requirement to current stage's user_requirement
  - "no"   → no inheritance needed

Reads previous stage output from:
  ~/.openclaw/workspace/autodna_store/stage_<N-1>_output_latest.txt

Environment:
  GEMINI_API_KEY  required
"""

import sys
import os
import json
import urllib.request
import urllib.error

STORE_DIR = os.path.expanduser("~/.openclaw/workspace/autodna_store")
TRUNCATE_LENGTH = 3000


def load_stage_output(stage_num: int) -> str:
    path = os.path.join(STORE_DIR, f"stage_{stage_num}_output_latest.txt")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read().strip()
    return ""


def call_gemini(prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set.", file=sys.stderr)
        sys.exit(1)

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash:generateContent?key={api_key}"
    )
    payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
    return data["candidates"][0]["content"]["parts"][0]["text"].strip().upper()


def main():
    if len(sys.argv) < 5:
        print(
            "Usage: judge_requirement_relevance.py <stage_num> "
            "'<prev_stage_name>' '<prev_requirement>' '<current_stage_name>'",
            file=sys.stderr,
        )
        sys.exit(1)

    current_stage_num = int(sys.argv[1])
    prev_stage_name = sys.argv[2]
    prev_requirement = sys.argv[3]
    current_stage_name = sys.argv[4]

    # If there is no previous requirement, nothing to inherit
    if not prev_requirement.strip():
        print("no")
        return

    prev_stage_num = current_stage_num - 1
    prev_result = load_stage_output(prev_stage_num)
    prev_result_snippet = prev_result[:TRUNCATE_LENGTH]

    prompt = f"""You are a scientific experiment planner.
Determine if the specific user requirement from the previous stage should be carried over and applied to the current stage.

Previous Stage: {prev_stage_name}
Previous Requirement: "{prev_requirement}"
Previous Result Summary: {prev_result_snippet}...

Current Stage: {current_stage_name}

Does the Previous Requirement constrain or apply to the Current Stage?
Output ONLY "YES" or "NO".
"""

    answer = call_gemini(prompt)

    if "YES" in answer:
        print("yes")
    else:
        print("no")


if __name__ == "__main__":
    main()
