import json

from app.models.evidence import Evidence
from app.engines.contradiction import detect_contradictions


with open("data/demo_case.json", "r") as file:
    data = json.load(file)


evidence = [
    Evidence(**item)
    for item in data["evidence"]
]


contradictions = detect_contradictions(evidence)


print("\n===== LUNA CONTRADICTIONS =====\n")


if not contradictions:
    print("No contradictions detected.")

else:
    for contradiction in contradictions:

        print(
            f"{contradiction.id} | "
            f"{contradiction.severity.upper()} | "
            f"{contradiction.description}"
        )

        print(
            f"   Evidence A: {contradiction.evidence_a}"
        )

        print(
            f"   Evidence B: {contradiction.evidence_b}"
        )

        print()