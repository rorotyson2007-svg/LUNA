from typing import Dict

from app.models.evidence import Evidence


def calculate_evidence_quality(evidence: Evidence) -> float:
    """
    Calculates the intrinsic quality of an evidence item.

    Factors:
    - reliability
    - directness
    - timestamp confidence
    """

    reliability = max(0.0, min(1.0, evidence.reliability))
    directness = max(0.0, min(1.0, evidence.directness))
    timestamp_confidence = max(
        0.0,
        min(1.0, evidence.timestamp_confidence)
    )

    quality = (
        reliability * 0.5
        + directness * 0.3
        + timestamp_confidence * 0.2
    )

    return round(quality, 3)


def calculate_contribution(
    evidence: Evidence,
    theory_id: str
) -> float:
    """
    Calculates how strongly an evidence item contributes
    to a specific theory.
    """

    quality = calculate_evidence_quality(evidence)

    if theory_id in evidence.supports_theories:
        return round(quality, 3)

    if theory_id in evidence.refutes_theories:
        return round(-quality, 3)

    return 0.0


def build_evidence_dna(
    evidence: Evidence,
    theory_ids: list[str]
) -> Dict:
    """
    Creates a complete Evidence DNA profile.
    """

    contributions = {}

    for theory_id in theory_ids:
        contributions[theory_id] = calculate_contribution(
            evidence,
            theory_id
        )

    evidence.contribution_scores = contributions

    return {
        "id": evidence.id,
        "type": evidence.type,
        "source": evidence.source,

        "quality": calculate_evidence_quality(evidence),

        "reliability": evidence.reliability,
        "directness": evidence.directness,
        "timestamp_confidence": evidence.timestamp_confidence,

        "dependencies": evidence.dependencies,
        "contradictions": evidence.contradictions,

        "supports_theories": evidence.supports_theories,
        "refutes_theories": evidence.refutes_theories,

        "contribution_scores": contributions,

        "status": evidence.status,
    }