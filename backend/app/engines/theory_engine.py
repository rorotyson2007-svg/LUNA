from app.reasoning.llm_client import generate_theories


def _serialize(item):
    """
    Convert Pydantic models or dictionaries into plain dictionaries.
    """
    if hasattr(item, "model_dump"):
        return item.model_dump()

    if isinstance(item, dict):
        return item

    if hasattr(item, "__dict__"):
        return item.__dict__

    return item


def run_theory_engine(
    evidence,
    timeline,
    contradictions,
    gaps,
):

    case_data = {
        "evidence": [
            _serialize(item)
            for item in evidence
        ],

        "timeline": [
            _serialize(item)
            for item in timeline
        ],

        "contradictions": [
            _serialize(item)
            for item in contradictions
        ],

        "gaps": [
            _serialize(item)
            for item in gaps
        ],
    }

    return generate_theories(case_data)