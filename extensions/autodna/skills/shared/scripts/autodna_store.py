#!/usr/bin/env python3
"""
AutoDNA shared store utility — inter-Skill data passing via filesystem.

Usage:
  write <skill_name>   Read from /tmp/autodna_skill_output.txt, save to store
  read  <skill_name>   Print stored content to stdout

Store location: ~/.openclaw/workspace/autodna_store/
Temp input file: /tmp/autodna_skill_output.txt

Skill name conventions:
  protocol    protocol-agent output
  reagent     reagent-agent output
  code        code-agent output
  hardware    hardware-agent output
  hypothesis  hypothesis-agent output
  literature  literature-agent output
"""
import sys
import os

STORE_DIR = os.path.expanduser("~/.openclaw/workspace/autodna_store")
TEMP_FILE = "/tmp/autodna_skill_output.txt"


def write(skill_name: str) -> None:
    os.makedirs(STORE_DIR, exist_ok=True)
    if not os.path.exists(TEMP_FILE):
        print(f"ERROR: {TEMP_FILE} not found. Write your content there first.")
        sys.exit(1)
    with open(TEMP_FILE, encoding="utf-8") as f:
        content = f.read()
    if not content.strip():
        print("ERROR: temp file is empty.")
        sys.exit(1)
    dest = os.path.join(STORE_DIR, f"{skill_name}_latest.txt")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(content)
    size = len(content)
    print(f"[STORED: {skill_name}_latest | {size} chars]")


def read(skill_name: str) -> None:
    path = os.path.join(STORE_DIR, f"{skill_name}_latest.txt")
    if not os.path.exists(path):
        print(
            f"[NOT FOUND: {skill_name}_latest — "
            f"the skill has not stored output yet or store was cleared]"
        )
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        content = f.read()
    print(content, end="")


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    skill = sys.argv[2]
    if cmd == "write":
        write(skill)
    elif cmd == "read":
        read(skill)
    else:
        print(f"ERROR: unknown command '{cmd}'. Use 'write' or 'read'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
