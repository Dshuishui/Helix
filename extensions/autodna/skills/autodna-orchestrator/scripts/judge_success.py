#!/usr/bin/env python3
"""
Judge whether the overall multi-stage experiment succeeded.
If failed, determine which stage to retry from.
Mirrors AutoDNA's judge_experiment_success() + analyze_failure_and_get_retry_stage().

Usage:
  judge_success.py "<initial_user_goal>" <total_stages>

Output (JSON):
  {
    "success": true/false,
    "failure_reason": "...",   (only if failed)
    "retry_stage": 2           (only if failed; -1 = no retry recommended)
  }

Reads stage outputs from:
  ~/.openclaw/workspace/autodna_store/stage_N_output_latest.txt

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
    return f"(Stage {stage_num} output not found)"


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
    if len(sys.argv) < 3:
        print(
            "Usage: judge_success.py '<initial_user_goal>' <total_stages>",
            file=sys.stderr,
        )
        sys.exit(1)

    initial_goal = sys.argv[1]
    total_stages = int(sys.argv[2])

    # Collect all stage outputs
    combined_outputs = ""
    for i in range(1, total_stages + 1):
        output = load_stage_output(i)
        combined_outputs += f"\n--- Stage {i} ---\n{output}\n"

    # Step 1: judge success
    success_prompt = f"""You are a scientific experiment evaluator. Based on the experiment final result, determine if the experiment was successful.

Final Result:
{combined_outputs}

Criteria for success:
- No critical errors or failures were reported
- The output contains meaningful results or conclusions

Output ONLY "YES" if the experiment is successful, or "NO" if it is not successful.
"""

    answer = call_gemini(success_prompt).upper()
    is_success = "YES" in answer

    if is_success:
        result = {"success": True}
        print(json.dumps(result))
        return

    # Step 2: analyze failure and recommend retry stage
    analysis_prompt = f"""You are a scientific experiment troubleshooter. The following experiment did not succeed. Analyze the outputs from each stage to determine:
1. Why the experiment was not successful
2. Which stage should be retried to fix the issue

Experiment Goal:
{initial_goal}

Stage Outputs:
{combined_outputs}

Analyze the failure and determine the earliest stage where the issue originated or where a retry would most likely fix the problem.

Output your analysis in the following format:
```json
{{
    "failure_reason": "Brief explanation of why the experiment failed",
    "retry_stage": <stage_number_to_retry_from>
}}
```

The retry_stage should be an integer representing the stage number (1-indexed). If the failure cannot be fixed by retrying, output retry_stage as -1.
"""

    raw = call_gemini(analysis_prompt)
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        analysis = json.loads(raw)
        failure_reason = analysis.get("failure_reason", "Unknown reason")
        retry_stage = int(analysis.get("retry_stage", -1))
    except (json.JSONDecodeError, ValueError, KeyError):
        failure_reason = "Failed to parse failure analysis"
        retry_stage = 1

    result = {
        "success": False,
        "failure_reason": failure_reason,
        "retry_stage": retry_stage,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
