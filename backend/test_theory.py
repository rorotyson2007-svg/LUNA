import json

from app.models.evidence import Evidence
from app.engines.timeline import build_timeline
from app.engines.contradiction import detect_contradictions
from app.engines.gaps import detect_evidence_gaps
from app.engines.theory_engine import run_theory_engine


# ---------------------------------------------------------
# Load case
# ---------------------------------------------------------

with open("data/demo_case.json", "r") as file:
    data = json.load(file)


# ---------------------------------------------------------
# Build evidence
# ---------------------------------------------------------

evidence = [
    Evidence(**item)
    for item in data["evidence"]
]


# ---------------------------------------------------------
# Build timeline
# ---------------------------------------------------------

timeline = build_timeline(evidence)


# ---------------------------------------------------------
# Detect contradictions
# ---------------------------------------------------------

contradictions = detect_contradictions(evidence)


# ---------------------------------------------------------
# Detect evidence gaps
# ---------------------------------------------------------

gaps = detect_evidence_gaps(evidence)


# ---------------------------------------------------------
# Run theory engine
# ---------------------------------------------------------

result = run_theory_engine(
    evidence=evidence,
    timeline=timeline,
    contradictions=contradictions,
    gaps=gaps
)


# ---------------------------------------------------------
# Display results
# ---------------------------------------------------------

print("\n========================================")
print("          LUNA CASE THEORIES")
print("========================================\n")


for theory in result.theories:

    print(f"{theory.id} | {theory.title}")

    print(f"Confidence: {theory.confidence}")
    print(f"Score: {theory.score}")

    print("\nExplanation:")
    print(theory.explanation)

    print("\nSupporting Evidence:")
    print(", ".join(theory.supporting_evidence))

    print("\nContradicting Evidence:")
    print(
        ", ".join(theory.contradicting_evidence)
        if theory.contradicting_evidence
        else "None identified"
    )

    print("\nAssumptions:")

    for assumption in theory.assumptions:
        print(f"  - {assumption}")

    print("\n----------------------------------------\n")