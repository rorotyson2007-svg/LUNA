from typing import Dict, Any


# ============================================================
# LUNA — NEXT BEST EVIDENCE ENGINE
# ============================================================

def get_value(obj, key, default=None):

    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(obj, key, default)


def rank_next_best_evidence(
    theories: list,
    evidence: list,
    red_team_report: dict,
    evidence_gaps: list,
) -> Dict[str, Any]:

    # ========================================================
    # CANDIDATE EVIDENCE
    # ========================================================

    candidates = [

        {
            "id": "NBE-01",
            "evidence_type": "CCTV footage",
            "description": (
                "Review Office A entry and exit CCTV footage "
                "between 14:09 and 14:20."
            ),
            "question": (
                "Did Person #B04 actually enter or leave "
                "Office A?"
            ),
            "target_theories": [
                "TH-01",
                "T01",
                "T02",
                "T03",
            ],
            "decisiveness": 0.95,
            "feasibility": 0.90,
        },

        {
            "id": "NBE-02",
            "evidence_type": "Access-control log",
            "description": (
                "Retrieve electronic door-access records "
                "for Office A between 14:09 and 14:20."
            ),
            "question": (
                "Was Office A accessed during the critical "
                "time window, and which credential was used?"
            ),
            "target_theories": [
                "TH-01",
                "T01",
                "T02",
            ],
            "decisiveness": 0.80,
            "feasibility": 0.95,
        },

        {
            "id": "NBE-03",
            "evidence_type": "CCTV footage",
            "description": (
                "Review service-corridor CCTV around "
                "14:12–14:20 to track Person #C09 and "
                "the cleaning cart."
            ),
            "question": (
                "Could the cleaning cart have been used "
                "to move LAPTOP-01?"
            ),
            "target_theories": [
                "TH-01",
                "T01",
                "T03",
            ],
            "decisiveness": 0.70,
            "feasibility": 0.90,
        },

        {
            "id": "NBE-04",
            "evidence_type": "Witness clarification",
            "description": (
                "Re-interview Witness-W02 regarding the "
                "14:12 Office A door event."
            ),
            "question": (
                "Can Witness-W02 provide additional "
                "information about who entered or left?"
            ),
            "target_theories": [
                "TH-01",
                "T01",
                "T02",
                "T03",
            ],
            "decisiveness": 0.55,
            "feasibility": 0.85,
        },

        {
            "id": "NBE-05",
            "evidence_type": "Physical evidence",
            "description": (
                "Inspect the Office A desk, surrounding "
                "area, and relevant storage locations "
                "for evidence of LAPTOP-01 relocation."
            ),
            "question": (
                "Was LAPTOP-01 moved from the desk rather "
                "than removed from the building?"
            ),
            "target_theories": [
                "TH-01",
                "T01",
                "T02",
                "T03",
            ],
            "decisiveness": 0.60,
            "feasibility": 0.80,
        },
    ]

    # ========================================================
    # ACTIVE THEORY IDS
    # ========================================================

    active_theory_ids = []

    for theory in theories:

        theory_id = get_value(
            theory,
            "id"
        )

        if theory_id:
            active_theory_ids.append(
                theory_id
            )

    theory_count = len(active_theory_ids)

    # ========================================================
    # SCORE CANDIDATES
    # ========================================================

    for candidate in candidates:

        affected_theories = [

            theory_id

            for theory_id
            in candidate["target_theories"]

            if theory_id
            in active_theory_ids
        ]

        if theory_count:

            coverage = (
                len(affected_theories)
                /
                theory_count
            )

        else:

            coverage = 0.0

        score = (
            candidate["decisiveness"] * 0.60
            +
            coverage * 0.25
            +
            candidate["feasibility"] * 0.15
        )

        candidate["affected_theories"] = (
            affected_theories
        )

        candidate["score"] = round(
            score,
            2
        )

    # ========================================================
    # SORT
    # ========================================================

    candidates.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    best = candidates[0]

    # ========================================================
    # THEORY IMPACT
    # ========================================================

    theory_impact = []

    for theory in theories:

        theory_id = get_value(
            theory,
            "id"
        )

        theory_title = get_value(
            theory,
            "title",
            "Unknown theory"
        )

        if theory_id not in best["affected_theories"]:
            continue

        # --------------------------------------------
        # TH-01 / T01
        # --------------------------------------------

        if theory_id in ["TH-01", "T01"]:

            impact = (
                "If CCTV shows B04 entering Office A, "
                "this theory becomes significantly stronger. "
                "If B04 never enters, the theory is weakened."
            )

        # --------------------------------------------
        # T02
        # --------------------------------------------

        elif theory_id == "T02":

            impact = (
                "If B04 is confirmed inside Office A, "
                "T02 becomes less likely as the primary "
                "explanation. If B04 is absent, T02 remains "
                "viable."
            )

        # --------------------------------------------
        # T03
        # --------------------------------------------

        elif theory_id == "T03":

            impact = (
                "If B04 is absent from Office A, the "
                "service-corridor explanation becomes "
                "relatively more plausible. If B04 enters, "
                "T03 loses relative support."
            )

        # --------------------------------------------
        # Generic theory
        # --------------------------------------------

        else:

            impact = (
                f"This evidence directly affects "
                f"{theory_title} by resolving an "
                f"unanswered part of its timeline."
            )

        theory_impact.append({

            "theory_id": theory_id,

            "impact": impact,

        })

    # ========================================================
    # PRIORITY
    # ========================================================

    if best["score"] >= 0.75:

        priority = "HIGH"

    elif best["score"] >= 0.50:

        priority = "MEDIUM"

    else:

        priority = "LOW"

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        "recommendation":
            best["description"],

        "evidence_type":
            best["evidence_type"],

        "investigative_question":
            best["question"],

        "score":
            best["score"],

        "priority":
            priority,

        "reason": (
            "This evidence has the highest expected "
            "ability to distinguish between the remaining "
            "investigation theories while remaining "
            "practical to obtain."
        ),

        "theory_impact":
            theory_impact,

        "ranked_candidates":
            candidates,
    }