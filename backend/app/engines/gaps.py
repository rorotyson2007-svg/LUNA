from typing import List, Dict

from app.models.evidence import Evidence


def detect_evidence_gaps(
    evidence: List[Evidence],
) -> List[Dict]:

    gaps = []

    for item in evidence:

        observation = item.observation.lower()

        uncertainty_phrases = [
            "does not show",
            "did not see",
            "not visible",
            "partially blocks",
            "unknown",
            "cannot determine"
        ]

        if any(
            phrase in observation
            for phrase in uncertainty_phrases
        ):

            gaps.append(
                {
                    "id": f"G{len(gaps) + 1:02d}",
                    "source_evidence": item.id,
                    "description": item.observation,
                    "type": "visibility_gap"
                }
            )

    return gaps