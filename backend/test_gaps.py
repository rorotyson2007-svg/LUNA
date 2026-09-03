import json

from app.models.evidence import Evidence
from app.engines.gaps import detect_evidence_gaps


with open("data/demo_case.json", "r") as file:
    data = json.load(file)


evidence = [
    Evidence(**item)
    for item in data["evidence"]
]


gaps = detect_evidence_gaps(evidence)


print("\n===== LUNA EVIDENCE GAPS =====\n")


for gap in gaps:

    print(
        f"{gap['id']} | "
        f"{gap['type']} | "
        f"Evidence {gap['source_evidence']}"
    )

    print(
        f"   {gap['description']}"
    )

    print()