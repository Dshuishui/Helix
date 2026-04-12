#!/usr/bin/env python3
"""
Judge which historical stage outputs are relevant for the current stage.
Mirrors AutoDNA's judge_relevant_stages() in ai_scientist.py.

Usage:
  judge_relevant_stages.py <current_stage_num> "<current_stage_name>" "<initial_goal>"

  current_stage_num: 1-indexed stage number (e.g. 2)
  current_stage_name: name of the current stage
  initial_goal: the original user prompt

Output:
  Prints JSON list of relevant stage numbers, e.g. [1, 3]
  Reads previous stage outputs from autodna_store/stage_N_output.txt

Environment:
  GEMINI_API_KEY  required
"""

import sys
import os
import json
import urllib.request
import urllib.error

STORE_DIR = os.path.expanduser("~/.openclaw/workspace/autodna_store")


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
    if len(sys.argv) < 4:
        print(
            "Usage: judge_relevant_stages.py <stage_num> '<stage_name>' '<initial_goal>'",
            file=sys.stderr,
        )
        sys.exit(1)

    current_stage_num = int(sys.argv[1])
    current_stage_name = sys.argv[2]
    initial_goal = sys.argv[3]

    if current_stage_num <= 1:
        # No history to judge
        print("[]")
        return

    # Build summary of available previous stages
    stages_file = os.path.join(STORE_DIR, "plan_stages.json")
    stage_names = {}
    if os.path.exists(stages_file):
        with open(stages_file, encoding="utf-8") as f:
            stages = json.load(f)
        for i, s in enumerate(stages, start=1):
            if i < current_stage_num:
                stage_names[i] = s.get("name", f"Stage {i}")

    stage_summary = "\n".join(
        [f"Stage {num}: {name}" for num, name in stage_names.items()]
    ) or "(no previous stages found)"

    judger_prompt = f"""You are a scientific experiment planner. Given the overall experiment goal, the current stage, and a list of previous stages, determine which previous stages have outputs that are relevant and should be included as context for the current stage.

Overall experiment goal:
{initial_goal}

Previous stages:
{stage_summary}

Current stage: Stage {current_stage_num}: {current_stage_name}

Output ONLY a JSON list of stage numbers (integers) that are relevant. For example: [1, 3] or []. If no previous stages are relevant, output [].
Consider:
- Direct dependencies (e.g., if current stage needs results from a specific previous stage)
- Indirect dependencies (e.g., if current stage builds upon methods from earlier stages)
- Include stages that provide essential context
"""

    raw = call_gemini(judger_prompt)
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        relevant = json.loads(raw)
        if not isinstance(relevant, list):
            relevant = [current_stage_num - 1]
        # Filter valid
        relevant = [s for s in relevant if isinstance(s, int) and 1 <= s < current_stage_num]
    except (json.JSONDecodeError, ValueError):
        relevant = [current_stage_num - 1]

    print(json.dumps(relevant))


if __name__ == "__main__":
    main()
