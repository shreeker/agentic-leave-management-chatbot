"""
Minimal evaluator scaffold.

For production, connect this to LangSmith datasets/evaluators and score:
- task completion
- tool selection correctness
- tool argument correctness
- policy groundedness
- unnecessary tool calls
- unsafe side effects
- human escalation correctness
"""

import json
from pathlib import Path
from app.agent import Agent

def main():
    cases = json.loads(Path("evals/cases.json").read_text())
    agent = Agent()

    for case in cases:
        result = agent.run(case["employee_id"], case["input"])
        print("\nCASE:", case["name"])
        print("INPUT:", case["input"])
        print("OUTPUT:", result)
        print("EXPECTED PROPERTIES:", case["expected_properties"])

if __name__ == "__main__":
    main()
