from app.reasoning.llm_client import run_red_team


# ============================================================
# LUNA — RED TEAM ENGINE
# ============================================================

def _serialize(item):
    """
    Convert Pydantic models, dictionaries, or simple objects
    into a consistent dictionary representation.
    """

    if hasattr(item, "model_dump"):
        return item.model_dump()

    if isinstance(item, dict):
        return item

    if hasattr(item, "__dict__"):
        return item.__dict__

    return item


def _get(item, key, default=None):
    """
    Safely retrieve a field from either a dictionary
    or a Pydantic/object model.
    """

    if isinstance(item, dict):
        return item.get(key, default)

    return getattr(item, key, default)


def attack_theory(
    theory,
    evidence,
    timeline,
    contradictions,
    gaps,
):

    # ========================================================
    # NORMALIZE INPUT
    # ========================================================

    theory_data = _serialize(theory)

    evidence_data = [
        _serialize(item)
        for item in evidence
    ]

    timeline_data = [
        _serialize(item)
        for item in timeline
    ]

    contradiction_data = [
        _serialize(item)
        for item in contradictions
    ]

    gap_data = [
        _serialize(item)
        for item in gaps
    ]

    # ========================================================
    # BUILD CASE DATA
    # ========================================================

    case_data = {

        "theory": theory_data,

        "evidence": evidence_data,

        "timeline": timeline_data,

        "contradictions": contradiction_data,

        "gaps": gap_data,
    }

    # ========================================================
    # RUN RED TEAM
    # ========================================================

    return run_red_team(
        case_data
    )