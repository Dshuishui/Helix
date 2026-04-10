#!/usr/bin/env python3
"""
AutoDNA Hardware Runner — auto-correction + execution + result collection.

Mirrors AutoDNA's Hardware Agent behavior:
  Phase 1: Correction loop (executor/corrector/ PYTHONPATH, strict mock)
           Run → stderr? → LLM fix → retry (max 3 attempts)
  Phase 2: Scheduler run (executor/scheduler/ PYTHONPATH, logging scheduler)
           Generates protocol_flow.json, reads results

Usage:
  run_experiment.py                   # reads scripts from autodna_store/code_latest.txt
  run_experiment.py <script_file.py>  # runs a single specified script

Environment variables:
  GEMINI_API_KEY   Required for auto-correction LLM calls
"""

import sys
import os
import re
import subprocess
import json
import urllib.request
import urllib.error
from datetime import datetime
from typing import Optional

# --- Paths ---
AUTODNA_SCIENTIST = os.path.expanduser(
    "~/Documents/Github/AutoDNA/AutoDNA-python/scientist"
)
CORRECTOR_DIR  = os.path.join(AUTODNA_SCIENTIST, "executor", "corrector")
SCHEDULER_DIR  = os.path.join(AUTODNA_SCIENTIST, "executor", "scheduler")

STORE_DIR       = os.path.expanduser("~/.openclaw/workspace/autodna_store")
CODE_STORE      = os.path.join(STORE_DIR, "code_latest.txt")
PROTOCOL_FLOW   = os.path.join(SCHEDULER_DIR, "protocol_flow.json")
SCRIPT_TMPDIR   = "/tmp/autodna_scripts"

MAX_CORRECTION_ATTEMPTS = 3   # matches AutoDNA's MAX_CORRECTION_ATTEMPTS

PYTHON = sys.executable

# --- Corrector prompt (matches AutoDNA's prompt_corrector template) ---
CORRECTOR_PROMPT_TEMPLATE = """\
You are a corrector responsible for correcting a code with slight modifications \
based on the original code provided. You must not change the overall structure \
and logic of the original code, only make necessary corrections. The output must \
be pure Python code (excluding any ``` mark), without any additional prints.

Original code to be corrected:
{original_code}

Error message:
{error_message}

Lab instrument controls and modules:
{hardware_abstractions}
{coder_hints}"""

CODER_HINTS = """\
Experiment Hints:
1. The concentration of components of the buffer provided is the concentration of 1X solution. \
All concentrations given in the experiment procedure are final concentrations in the reaction mixture.
2. Keep the volume of the reaction mixture consistent unless specified.
3. When using an instrument, choose the default setting value if not explicitly specified.
Coding Hints:
1. Directly import `lab_modules`. Use as much modules from `lab_modules` directly as possible. \
Do not modify the existing modules.
2. Use `print` to print the detailed final results. Do not use `print` for any debugging or \
intermediate steps. If the final results contain containers, print their label and volume.
3. For equipment settings, you must adhere to the equipment usage guidance provided in the \
code description.
4. Do not add any error handlings. Use as least comments as possible."""


# ── Utilities ──────────────────────────────────────────────────────────────────

def extract_python_code(text: str) -> str:
    """Strip markdown fences if present."""
    text = text.strip()
    if text.startswith("```python"):
        text = text[len("```python"):].strip()
    if text.startswith("```"):
        text = text[3:].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    return text


def run_script_with_env(code: str, lib_path: str, label: str) -> dict:
    """Run code string with specified PYTHONPATH, return result dict."""
    # Save to temp file
    tmp_path = os.path.join(SCRIPT_TMPDIR, f"_tmp_{label}.py")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(code)

    env = os.environ.copy()
    env["PYTHONPATH"] = lib_path + os.pathsep + env.get("PYTHONPATH", "")
    env["SCHEDULER_CONFIG_PATH"] = SCHEDULER_DIR

    try:
        result = subprocess.run(
            [PYTHON, tmp_path],
            capture_output=True, text=True, env=env, timeout=600
        )
        return {
            "success": result.returncode == 0 and not result.stderr.strip(),
            "stdout": result.stdout,
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": "Timeout after 10 min", "returncode": -1}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}


def load_hardware_abstractions() -> str:
    """Load lab_modules.py content for corrector context."""
    path = os.path.join(SCHEDULER_DIR, "lab_modules.py")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            content = f.read()
        return content[:4000]   # truncate to keep prompt size reasonable
    return "(lab_modules.py not found)"


def call_llm_corrector(original_code: str, error_message: str) -> Optional[str]:
    """
    Call Gemini API to auto-correct a script.
    Matches AutoDNA's corrector() function behavior.
    Returns corrected code string, or None if API call fails.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("  [WARN] GEMINI_API_KEY not set — skipping LLM correction.")
        return None

    hw = load_hardware_abstractions()
    prompt = CORRECTOR_PROMPT_TEMPLATE.format(
        original_code=original_code,
        error_message=error_message,
        hardware_abstractions=hw,
        coder_hints=CODER_HINTS,
    )

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash:generateContent?key={api_key}"
    )
    payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        raw = data["candidates"][0]["content"]["parts"][0]["text"]
        return extract_python_code(raw)
    except urllib.error.HTTPError as e:
        print(f"  [ERROR] LLM API HTTP error: {e.code} {e.reason}")
        return None
    except Exception as e:
        print(f"  [ERROR] LLM correction failed: {e}")
        return None


# ── Core: correction loop + scheduler run ──────────────────────────────────────

def run_with_correction(script_code: str, script_index: int) -> dict:
    """
    Phase 1 — Correction loop (corrector mock, strict):
      Run → stderr? → LLM fix → retry (max MAX_CORRECTION_ATTEMPTS)
    Phase 2 — Scheduler run (logging scheduler, generates protocol_flow.json)

    Returns final result dict with keys: success, stdout, stderr, final_code,
    correction_attempts, phase2_result.
    """
    current_code = script_code
    correction_attempts = 0

    print(f"\n{'='*60}")
    print(f"Script {script_index}: Correction phase (corrector mock)")
    print(f"{'='*60}")

    # Phase 1: correction loop
    for attempt in range(1, MAX_CORRECTION_ATTEMPTS + 1):
        print(f"  Attempt {attempt}/{MAX_CORRECTION_ATTEMPTS} ...", end=" ")
        result = run_script_with_env(current_code, CORRECTOR_DIR, f"s{script_index}_c{attempt}")

        if result["success"]:
            print("OK")
            break
        else:
            print(f"FAILED\n  Error: {result['stderr'][:200]}")
            if attempt < MAX_CORRECTION_ATTEMPTS:
                print(f"  → Calling LLM to auto-correct...")
                corrected = call_llm_corrector(current_code, result["stderr"])
                if corrected:
                    current_code = corrected
                    correction_attempts += 1
                    print(f"  → Correction applied.")
                else:
                    print(f"  → LLM correction unavailable, stopping.")
                    break
    else:
        # All attempts exhausted
        print(f"  All {MAX_CORRECTION_ATTEMPTS} correction attempts exhausted.")

    correction_ok = result["success"]

    # Phase 2: scheduler run (generates protocol_flow.json)
    print(f"\nScript {script_index}: Scheduler run (generates protocol_flow.json)")
    phase2 = run_script_with_env(current_code, SCHEDULER_DIR, f"s{script_index}_scheduler")
    print(f"  Return code: {phase2['returncode']}")
    if phase2["stdout"]:
        print(f"  Output: {phase2['stdout'].strip()}")
    if phase2["stderr"]:
        print(f"  Stderr: {phase2['stderr'][:200]}")

    return {
        "success": phase2["returncode"] == 0,
        "correction_ok": correction_ok,
        "correction_attempts": correction_attempts,
        "stdout": phase2["stdout"],
        "stderr": phase2["stderr"],
        "returncode": phase2["returncode"],
        "final_code": current_code,
    }


# ── Results parsing ─────────────────────────────────────────────────────────────

def read_protocol_flow() -> Optional[dict]:
    """Read protocol_flow.json after a scheduler run."""
    if not os.path.exists(PROTOCOL_FLOW):
        return None
    with open(PROTOCOL_FLOW, encoding="utf-8") as f:
        return json.load(f)


def summarize_flow(flow: Optional[dict]) -> str:
    """Extract key metrics from protocol_flow.json."""
    if not flow:
        return "  No protocol_flow.json generated."

    steps = flow.get("steps", [])
    lines = [f"  Steps executed: {len(steps)}"]

    fluoro = [s for s in steps if s.get("action") == "fluorometer_measure"]
    if fluoro:
        lines.append(f"  Fluorometer measurements: {len(fluoro)}")
        for s in fluoro:
            lines.append(f"    Step {s['id']}: {s.get('parameters', {})}")
    else:
        lines.append("  Fluorometer: no measurements (mock: -1 expected on real hardware)")

    allocs = [s for s in steps if s.get("action") == "container_allocate"]
    if allocs:
        last = allocs[-3:]
        lines.append(f"  Output containers ({len(allocs)} total, last {len(last)}):")
        for s in last:
            p = s.get("parameters", {})
            lines.append(f"    {p.get('container_label','?')} ({p.get('container_type','?')})")

    return "\n".join(lines)


# ── Script extraction ───────────────────────────────────────────────────────────

def extract_scripts(code_text: str) -> list:
    """Parse ## SCRIPT START ## blocks from Code Agent output."""
    scripts = []
    pattern = re.compile(
        r"## SCRIPT START ##\s*\n(# Path Description:.*?)\n(.*?)(?=## SCRIPT START ##|\Z)",
        re.DOTALL,
    )
    for i, m in enumerate(pattern.finditer(code_text), start=1):
        desc = m.group(1).replace("# Path Description:", "").strip()
        code = m.group(2).strip()
        scripts.append({"index": i, "description": desc, "code": code})
    return scripts


# ── Main ────────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(SCRIPT_TMPDIR, exist_ok=True)

    # Single script mode
    if len(sys.argv) > 1:
        script_path = sys.argv[1]
        if not os.path.exists(script_path):
            print(f"ERROR: {script_path} not found.")
            sys.exit(1)
        with open(script_path, encoding="utf-8") as f:
            code = f.read()
        result = run_with_correction(code, 1)
        flow = read_protocol_flow()
        print("\n=== Results from protocol_flow.json ===")
        print(summarize_flow(flow))
        return

    # Batch mode: read from code store
    if not os.path.exists(CODE_STORE):
        print(f"ERROR: {CODE_STORE} not found. Run Code Agent first.")
        sys.exit(1)

    with open(CODE_STORE, encoding="utf-8") as f:
        code_text = f.read()

    scripts = extract_scripts(code_text)
    if not scripts:
        print("ERROR: No ## SCRIPT START ## blocks found in code_latest.txt.")
        sys.exit(1)

    print(f"Found {len(scripts)} script(s). Starting correction + execution.\n")

    all_results = []
    for s in scripts:
        run_result = run_with_correction(s["code"], s["index"])
        flow = read_protocol_flow()
        flow_summary = summarize_flow(flow)
        all_results.append({
            "index": s["index"],
            "description": s["description"],
            "run": run_result,
            "flow_summary": flow_summary,
        })

    # Final consolidated summary
    print(f"\n{'='*60}")
    print("EXPERIMENT SUMMARY")
    print(f"{'='*60}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Scripts: {len(all_results)}")
    gemini_ok = bool(os.environ.get("GEMINI_API_KEY"))
    print(f"Auto-correction LLM: {'enabled (Gemini)' if gemini_ok else 'disabled (set GEMINI_API_KEY to enable)'}")
    print()

    for r in all_results:
        status = "SUCCESS" if r["run"]["success"] else "FAILED"
        corr = r["run"]["correction_attempts"]
        print(f"Script {r['index']} [{status}] (corrections: {corr}): {r['description']}")
        print(r["flow_summary"])
        if not r["run"]["success"] and r["run"]["stderr"]:
            print(f"  Last error: {r['run']['stderr'][:300]}")
        print()


if __name__ == "__main__":
    main()
