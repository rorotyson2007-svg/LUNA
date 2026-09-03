from app.pipeline import run_luna_pipeline


# ============================================================
# LUNA END-TO-END TEST DATA
# ============================================================

evidence = [
    {
        "id": "E01",
        "source": "CAM-01",
        "timestamp": "14:03",
        "description": (
            "Person #A17 enters Office A. "
            "LAPTOP-01 is visible on the desk."
        ),
    },
    {
        "id": "E02",
        "source": "Access-Control",
        "timestamp": "14:07",
        "description": (
            "CARD-17 records access to Office A."
        ),
    },
    {
        "id": "E03",
        "source": "CAM-01",
        "timestamp": "14:09",
        "description": (
            "Person #A17 leaves Office A. "
            "No laptop is visibly carried."
        ),
    },
    {
        "id": "E04",
        "source": "Witness-W01",
        "timestamp": "14:10",
        "description": (
            "Witness reports seeing Person #B04 "
            "walking toward the Office A corridor "
            "carrying a dark rectangular bag."
        ),
    },
    {
        "id": "E05",
        "source": "CAM-02",
        "timestamp": "14:11",
        "description": (
            "Person #B04 walks toward the Office A corridor. "
            "Camera does not show whether B04 enters Office A."
        ),
    },
    {
        "id": "E06",
        "source": "Witness-W02",
        "timestamp": "14:12",
        "description": (
            "Witness reports hearing the Office A "
            "door open and close but did not see who entered."
        ),
    },
    {
        "id": "E07",
        "source": "CAM-03",
        "timestamp": "14:14",
        "description": (
            "Person #C09 passes through the service corridor "
            "pushing a cleaning cart. The cart partially "
            "blocks the camera view."
        ),
    },
    {
        "id": "E08",
        "source": "Inventory-System",
        "timestamp": "14:20",
        "description": (
            "LAPTOP-01 is reported missing from its "
            "assigned desk in Office A."
        ),
    },
    {
        "id": "E09",
        "source": "CAM-01",
        "timestamp": "14:21",
        "description": (
            "Person #A17 returns to Office A."
        ),
    },
    {
        "id": "E10",
        "source": "CAM-01",
        "timestamp": "14:22",
        "description": (
            "Person #A17 inspects the desk area."
        ),
    },
]


timeline = [
    {
        "time": "14:03",
        "event": "A17 enters Office A; laptop visible.",
    },
    {
        "time": "14:09",
        "event": "A17 leaves Office A.",
    },
    {
        "time": "14:10",
        "event": "B04 approaches Office A corridor carrying BAG-01.",
    },
    {
        "time": "14:11",
        "event": "B04 continues toward Office A corridor.",
    },
    {
        "time": "14:12",
        "event": "Office A door opens and closes; identity unknown.",
    },
    {
        "time": "14:14",
        "event": "C09 passes service corridor with cleaning cart.",
    },
    {
        "time": "14:20",
        "event": "Laptop reported missing.",
    },
]


contradictions = []


gaps = [
    "No evidence establishes that B04 entered Office A.",
    "No evidence establishes who opened the Office A door at 14:12.",
    "No direct observation establishes when LAPTOP-01 left the office.",
    "Service corridor camera view is partially obstructed.",
]


# ============================================================
# RUN COMPLETE LUNA PIPELINE
# ============================================================

result = run_luna_pipeline(
    evidence=evidence,
    timeline=timeline,
    contradictions=contradictions,
    gaps=gaps,
)


# ============================================================
# DISPLAY FINAL RESULT
# ============================================================

print()
print("=" * 60)
print("                         🌙 LUNA")
print("=" * 60)

print()
print("              INVESTIGATION ANALYSIS")
print()

# ============================================================
# THEORIES
# ============================================================

print("=" * 60)
print("                    🧠 CASE THEORIES")
print("=" * 60)

for theory in result["theories"]:

    theory_id = (
        theory.id
        if hasattr(theory, "id")
        else theory.get("id")
    )

    title = (
        theory.title
        if hasattr(theory, "title")
        else theory.get("title")
    )

    score = (
        theory.score
        if hasattr(theory, "score")
        else theory.get("score")
    )

    print()
    print(f"{theory_id} | {title}")
    print(f"Score: {score}")


# ============================================================
# LEADING THEORY
# ============================================================

leading = result["leading_theory"]

leading_id = (
    leading.id
    if hasattr(leading, "id")
    else leading.get("id")
)

leading_title = (
    leading.title
    if hasattr(leading, "title")
    else leading.get("title")
)

print()
print("=" * 60)
print("                  🏆 LEADING THEORY")
print("=" * 60)

print()
print(f"{leading_id} | {leading_title}")


# ============================================================
# RED TEAM
# ============================================================

red_team = result["red_team"]

print()
print("=" * 60)
print("                    🔴 RED TEAM")
print("=" * 60)

print()
print(f"THEORY: {red_team.theory_id}")
print(f"VERDICT: {red_team.verdict}")

print()
print("UNSUPPORTED CLAIMS:")

for item in red_team.unsupported_claims:
    print(f"  ⚠ {item}")

print()
print("ASSUMPTIONS:")

for item in red_team.assumptions:
    print(f"  ⚠ {item}")

print()
print("ALTERNATIVE EXPLANATIONS:")

for item in red_team.alternative_explanations:
    print(f"  → {item}")

print()
print("CRITICAL QUESTIONS:")

for item in red_team.critical_questions:
    print(f"  ? {item}")

print()
print("EVIDENCE GAPS:")

for item in red_team.evidence_gaps:
    print(f"  ? {item}")


# ============================================================
# NEXT BEST EVIDENCE
# ============================================================

nbe = result["next_best_evidence"]

print()
print("=" * 60)
print("                🎯 NEXT BEST EVIDENCE")
print("=" * 60)

print()

print("RECOMMENDATION:")
print(nbe["recommendation"])

print()

print("INVESTIGATIVE QUESTION:")
print(nbe["investigative_question"])

print()

print(f"DISCRIMINATION SCORE: {nbe['score']}")
print(f"PRIORITY: {nbe['priority']}")

print()

print("WHY:")
print(nbe["reason"])

print()
print("THEORY IMPACT:")

for impact in nbe["theory_impact"]:

    print(
        f"  → {impact['theory_id']}: "
        f"{impact['impact']}"
    )


# ============================================================
# FINAL
# ============================================================

print()
print("=" * 60)
print("              🌙 LUNA ANALYSIS COMPLETE")
print("=" * 60)

print()
print(
    "Evidence → Theories → Red Team → "
    "Evidence Gaps → Next Best Evidence"
)

print()