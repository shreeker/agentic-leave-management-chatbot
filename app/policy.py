from pathlib import Path

POLICIES = [
    {
        "id": "VAC-001",
        "title": "Vacation Leave",
        "text": """
Vacation leave is available to eligible employees. Employees must have
sufficient available vacation balance. Requests of more than 5 working
days require manager approval. Employees should normally submit vacation
requests at least 10 working days before the start date.
"""
    },
    {
        "id": "SICK-001",
        "title": "Sick Leave",
        "text": """
Sick leave may be requested for illness. Manager approval is not required
before taking emergency sick leave, but the employee should notify the
manager as soon as reasonably possible. Supporting documentation may be
required under local policy.
"""
    },
    {
        "id": "CARRY-001",
        "title": "Carry Forward",
        "text": """
Unused vacation may be carried forward subject to the employee's local
employment policy and annual limits. The authoritative HR system is the
source of truth for the actual available balance.
"""
    },
    {
        "id": "PROB-001",
        "title": "Probation",
        "text": """
Employees in probation may request leave subject to applicable local
policy and manager approval requirements. The agent must retrieve the
applicable policy instead of assuming a universal probation rule.
"""
    },
]

def search_policy(query: str, top_k: int = 3):
    # Deterministic lightweight fallback retrieval for the demo.
    # Replace with Chroma/OpenSearch/Bedrock Knowledge Bases in production.
    terms = set(query.lower().split())
    scored = []
    for p in POLICIES:
        score = sum(1 for t in terms if t in p["text"].lower() or t in p["title"].lower())
        scored.append((score, p))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {"id": p["id"], "title": p["title"], "text": p["text"], "score": score}
        for score, p in scored[:top_k]
    ]
