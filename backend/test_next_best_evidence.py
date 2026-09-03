from app.engines.next_best_evidence import (
    rank_next_best_evidence
)


# ============================================================
# MOCK THEORIES
# ============================================================

theories = [

    {
        "id": "TH-01",
        "title": "Unauthorized Removal by Person B04",
    },

    {
        "id": "T02",
        "title": "Relocation during A17's presence",
    },

    {
        "id": "T03",
        "title": "Removal through service corridor",
    },
]


# ============================================================
# MOCK EVIDENCE
# ============================================================

evidence = []


# ============================================================
# MOCK RED TEAM
# ============================================================

red_team_report = {
    "verdict": "PLAUSIBLE",

    "evidence_gaps": [
        "No evidence establishes that B04 entered Office A.",
        "No evidence directly connects B04 to LAPTOP-01.",
    ],
}


# ============================================================
# GAPS
# ============================================================

evidence_gaps = [

    "No evidence establishes that B04 entered Office A.",

    "No evidence establishes who opened the Office A door.",

    "No direct observation establishes when "
    "LAPTOP-01 left the office.",
]


# ============================================================
# RUN
# ============================================================

result = rank_next_best_evidence(

    theories=theories,

    evidence=evidence,

    red_team_report=red_team_report,

    evidence_gaps=evidence_gaps,
)


# ============================================================
# DISPLAY
# ============================================================

print()
print("=" * 55)
print("             🎯 NEXT BEST EVIDENCE")
print("=" * 55)

print()

print(
    "RECOMMENDATION:"
)

print(
    result["recommendation"]
)

print()

print(
    "EVIDENCE TYPE:"
)

print(
    result["evidence_type"]
)

print()

print(
    "INVESTIGATIVE QUESTION:"
)

print(
    result["investigative_question"]
)

print()

print(
    f"DISCRIMINATION SCORE: "
    f"{result['score']}"
)

print(
    f"PRIORITY: "
    f"{result['priority']}"
)

print()

print(
    "WHY:"
)

print(
    result["reason"]
)

print()

print(
    "THEORY IMPACT:"
)

for impact in result["theory_impact"]:

    print(
        f"  → {impact['theory_id']}: "
        f"{impact['impact']}"
    )

print()

print("=" * 55)
print("             RANKED EVIDENCE")
print("=" * 55)

for index, candidate in enumerate(
    result["ranked_candidates"],
    start=1,
):

    print()

    print(
        f"{index}. "
        f"{candidate['evidence_type']}"
    )

    print(
        f"   Score: {candidate['score']}"
    )

    print(
        f"   {candidate['description']}"
    )

print()