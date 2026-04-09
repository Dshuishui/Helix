#!/opt/anaconda3/envs/autodna/bin/python
"""
Literature Agent query script.
Usage: python query_literature.py "<question>" "<experiment_name>" [paper_dir]

paper_dir options:
  final     - general papers (~411 PDFs)
  paper400  - DNA storage papers (~412 PDFs)
  manuals   - lab manuals (10 PDFs)
  (default: final)
"""

import sys
import os

PAPER_QA_PATH = "/Users/cong/Documents/Github/AutoDNA/AutoDNA-python/Lib/paper-qa"
sys.path.insert(0, PAPER_QA_PATH)

PAPERS_BASE = "/Users/cong/Documents/Github/AutoDNA/AutoDNA-python/scientist/papers"

def main():
    if len(sys.argv) < 3:
        print("Usage: query_literature.py <question> <experiment_name> [paper_dir]")
        sys.exit(1)

    question = sys.argv[1]
    experiment_name = sys.argv[2]
    paper_dir_name = sys.argv[3] if len(sys.argv) > 3 else "final"

    paper_directory = os.path.join(PAPERS_BASE, paper_dir_name)
    if not os.path.isdir(paper_directory):
        print(f"ERROR: Paper directory not found: {paper_directory}")
        sys.exit(1)

    # Gemini API key must be set in environment
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not gemini_key:
        print("ERROR: GEMINI_API_KEY environment variable is not set.")
        sys.exit(1)

    from paperqa import Settings, ask
    from paperqa.settings import AgentSettings

    full_question = (
        question
        + f"\nThe focus is on {experiment_name}, remove irrelevant information."
        + "\nProvide detailed, specific answers with accurate details as stated in the papers."
    )

    settings = Settings(
        llm="gemini/gemini-2.0-flash",
        summary_llm="gemini/gemini-2.0-flash",
        agent=AgentSettings(
            agent_llm="gemini/gemini-2.0-flash",
            index_concurrency=3,
        ),
        paper_directory=paper_directory,
        use_absolute_paper_directory=True,
        embedding="gemini/text-embedding-004",
        embedding_config={"trust_remote_code": True},
        verbosity=1,
    )
    settings.answer.answer_max_sources = 30
    settings.answer.evidence_k = 50
    settings.agent.search_count = 16
    settings.parsing.chunk_size = 8000
    settings.parsing.overlap = 700
    settings.answer.answer_length = (
        "YOUR ANSWER MUST BE STRICTLY IDENTICAL AS WHAT IS IN THE PAPER, WITH ACCURATE DETAILS."
    )

    try:
        answer_response = ask(query=full_question, settings=settings)
        print(answer_response.session.answer)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
