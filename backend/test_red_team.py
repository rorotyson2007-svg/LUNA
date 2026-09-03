import json

from app.models.evidence import Evidence

from app.engines.timeline import build_timeline

from app.engines.contradiction import (
    detect_contradictions
)

from app.engines.gaps import (
    detect_evidence_gaps
)

from app.engines.theory_engine import (
    run_theory_engine
)

from app.engines.red_team import (
    attack_theory
)


# ---------------------------------------------------------
# Load case
# ---------------------------------------------------------

with open("data/demo_case.json", "r") as file:
    data = json.load(file)


# ---------------------------------------------------------
# Evidence
# ---------------------------------------------------------

evidence = [
    Evidence(**item)
    for item in data["evidence"]
]


# ---------------------------------------------------------
# Timeline
# ---------------------------------------------------------

timeline = build_timeline(evidence)


# ---------------------------------------------------------
# Contradictions
# ---------------------------------------------------------

contradictions = detect_contradictions(
    evidence
)


# ---------------------------------------------------------
# Evidence gaps
# ---------------------------------------------------------

gaps = detect_evidence_gaps(
    evidence
)


# ---------------------------------------------------------
# Generate theories
# ---------------------------------------------------------

theories = run_theory_engine(
    evidence=evidence,
    timeline=timeline,
    contradictions=contradictions,
    gaps=gaps
)


# ---------------------------------------------------------
# Select leading theory
# ---------------------------------------------------------

leading_theory = max(
    theories.theories,
    key=lambda theory: theory.score
)


print("\n========================================")
print("             LEADING THEORY")
print("========================================\n")

print(
    f"{leading_theory.id} | "
    f"{leading_theory.title}"
)

print(
    f"Score: {leading_theory.score}"
)


# ---------------------------------------------------------
# RED TEAM
# ---------------------------------------------------------

report = attack_theory(
    theory=leading_theory,
    evidence=evidence,
    timeline=timeline,
    contradictions=contradictions,
    gaps=gaps
)


# ---------------------------------------------------------
# Display
# ---------------------------------------------------------

print("\n========================================")
print("             🔴 RED TEAM")
print("========================================\n")

print(
    f"THEORY: {report.theory_id}"
)

print(
    f"VERDICT: {report.verdict}"
)


print("\nSTRENGTHS:")

for item in report.strengths:
    print(f"  ✓ {item}")


print("\nUNSUPPORTED CLAIMS:")

for item in report.unsupported_claims:
    print(f"  ⚠ {item}")


print("\nCONTRADICTIONS:")

for item in report.contradictions:
    print(f"  ✕ {item}")


print("\nASSUMPTIONS:")

for item in report.assumptions:
    print(f"  ⚠ {item}")


print("\nALTERNATIVE EXPLANATIONS:")

for item in report.alternative_explanations:
    print(f"  → {item}")


print("\nCRITICAL QUESTIONS:")

for item in report.critical_questions:
    print(f"  ? {item}")


print("\nEVIDENCE GAPS:")

for item in report.evidence_gaps:
    print(f"  ? {item}")