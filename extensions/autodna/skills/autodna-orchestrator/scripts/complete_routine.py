#!/usr/bin/env python3
"""
Summarize all stage protocols into a final write summary.
Mirrors AutoDNA's complete_routine() in ai_scientist.py.

Called after all stages complete in a DNA Storage Write experiment.
Reads protocol output from each stage, summarizes key characteristics,
and saves the result as write_summary for subsequent Read experiments.

Usage:
  complete_routine.py <total_stages>

Output:
  Prints the generated summary to stdout.
  Saves to ~/.openclaw/workspace/autodna_store/write_summary_latest.txt

Reads from:
  ~/.openclaw/workspace/autodna_store/protocol_stage_N_latest.txt  (preferred)
  ~/.openclaw/workspace/autodna_store/stage_N_output_latest.txt    (fallback)

Environment:
  GEMINI_API_KEY  required
"""

import sys
import os
import json
import urllib.request
import urllib.error

STORE_DIR = os.path.expanduser("~/.openclaw/workspace/autodna_store")
WRITE_SUMMARY_FILE = os.path.join(STORE_DIR, "write_summary_latest.txt")

ALL_PROTOCOLS_SUMMARY_PROMPT = """\
{protocol_contents}
----------------------------------------------
Above is all the protocol executed.
Now there are next steps that requires the result of the protocols above, you must summarize the Key Characteristics of the product that went through the protocols above. The answer must be concise without mentioning the initial input.
"""


def load_stage_protocol(stage_num: int) -> str:
    """Load protocol content for a given stage. Prefers protocol_stage_N, falls back to stage_N_output."""
    protocol_path = os.path.join(STORE_DIR, f"protocol_stage_{stage_num}_latest.txt")
    if os.path.exists(protocol_path):
        with open(protocol_path, encoding="utf-8") as f:
            return f.read().strip()

    # Fallback: use the full stage output
    output_path = os.path.join(STORE_DIR, f"stage_{stage_num}_output_latest.txt")
    if os.path.exists(output_path):
        with open(output_path, encoding="utf-8") as f:
            return f.read().strip()

    return f"(Stage {stage_num} protocol not found)"


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
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def main():
    if len(sys.argv) < 2:
        print("Usage: complete_routine.py <total_stages>", file=sys.stderr)
        sys.exit(1)

    total_stages = int(sys.argv[1])

    # Collect protocol contents from each stage
    protocol_contents = ""
    for i in range(1, total_stages + 1):
        content = load_stage_protocol(i)
        if content:
            protocol_contents += f"--- Stage {i} Protocol ---\n{content}\n\n"

    if not protocol_contents.strip():
        print("ERROR: No protocol content found for any stage.", file=sys.stderr)
        sys.exit(1)

    prompt = ALL_PROTOCOLS_SUMMARY_PROMPT.format(protocol_contents=protocol_contents)
    summary = call_gemini(prompt)

    # Save write summary for Read experiments to consume
    os.makedirs(STORE_DIR, exist_ok=True)
    with open(WRITE_SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"[STORED: write_summary_latest | {len(summary)} chars]")
    print()
    print(summary)


if __name__ == "__main__":
    main()
